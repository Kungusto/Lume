class ServiceForTests:
    """Позже тут появятся полезные функции для удобочитаемости тестов"""


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
                image_key = f"books/{book_id}/images/page_{page_num + 1}_img_{img_index + 1}.png"
                result.append({"Body": image_bytes, "Key": image_key})
        return result
