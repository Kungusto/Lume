from pathlib import Path
from typing import List, Tuple

import aiofiles
from src.exceptions.books import PageNotFoundException
from src.exceptions.conftest import DirectoryNotFoundException, ReadFileException
from src.exceptions.files import FileNotFoundException


class PDFRenderer:
    """Работа с файлами .pdf"""

    @staticmethod
    def parse_images_from_pdf(doc, book_id: int):
        result = []
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            images_list = page.get_images(full=True)
            for img_index, img in enumerate(images_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_key = (
                    f"books/{book_id}/images/page_{page_num}_img_{img_index}.png"
                )
                result.append({"Body": image_bytes, "Key": image_key})
        return result

    @staticmethod
    def parse_text_end_images_from_page(doc, page_number: int, book_id: int):
        try:
            page = doc.load_page(page_number - 1)
        except ValueError as ex:
            raise PageNotFoundException(page_number=page_number) from ex
        blocks = page.get_text("dict")["blocks"]
        content: list[dict[str, str]] = []
        count_images = 0
        for block in blocks:
            if block["type"] == 0:
                for line in block.get("lines", []):
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                    if line_text.strip():
                        content.append(
                            {
                                "type": "text",
                                "content": line_text,  # сам текст
                                "size": span.get("size"),  # размер шрифта
                                "flags": span.get("flags"),  # флаги шрифта
                                "bidi": span.get(
                                    "bidi"
                                ),  # уровень двунаправленного текста
                                "char_flags": span.get("char_flags"),  # флаги символов
                                "font": span.get("font"),  # название шрифта
                                "color": span.get(
                                    "color"
                                ),  # цвет текста (в формате RGB)
                                "alpha": span.get("alpha"),  # прозрачность
                                "ascender": span.get(
                                    "ascender"
                                ),  # высота восходящей части шрифта
                                "descender": span.get(
                                    "descender"
                                ),  # высота нисходящей части шрифта
                                "origin": span.get(
                                    "origin"
                                ),  # координаты начала (x, y)
                                "bbox": span.get("bbox"),
                            }
                        )
            elif block["type"] == 1:
                content.append(
                    {
                        "type": "image",
                        "path": f"books/{book_id}/images/page_{page_number - 1}_img_{count_images}.png",
                        "bbox": block.get("bbox"),
                        "mask": block.get("mask"),
                        "width": block.get("width"),
                        "height": block.get("height"),
                    }
                )
                count_images += 1
        return content


class FileManager:
    STATIC_ROOT = Path("src/static")

    async def get_file_by_rel_path(self, rel_path: str) -> bytes:
        """
        Получает - относительный путь для директории src/static
        Возваращает - bytes нужного файла
        """
        file_path = self.STATIC_ROOT / rel_path
        if not file_path.exists():
            raise FileNotFoundException(file_path=file_path)
        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()
        return content

    async def get_files_in_folder(self, folder_path: str) -> List[Tuple[bytes, str]]:
        full_folder_path = self.STATIC_ROOT / folder_path
        files_data = []
        try:
            for file_path in full_folder_path.iterdir():
                if not file_path.is_file():
                    continue
                async with aiofiles.open(file_path, "rb") as f:
                    content = await f.read()
                    files_data.append((content, file_path.name))
        except OSError as ex:
            raise ReadFileException(filename=file_path.name) from ex
        return files_data

    @staticmethod
    def get_list_files_by_folder_path(folder_path: str) -> set[str]:
        """
        Получает - абсолютный путь к директории
        Возвращает - set() файлов в директории
        """
        try:
            return set(f.name for f in Path(folder_path).iterdir() if f.is_file())
        except FileNotFoundError as ex:
            raise DirectoryNotFoundException(folder_path=folder_path) from ex
