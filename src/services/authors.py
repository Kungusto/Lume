from time import time
from fastapi import UploadFile
from src.exceptions.files import (
    WrongCoverResolutionException,
    WrongFileExpensionException,
)
from src.models.books import BooksTagsORM
from src.services.base import BaseService
from src.services.auth import AuthService
from src.schemas.books import BookAddWithAuthorsTagsGenres, BookPATCHOnPublication
from src.schemas.books import (
    BookAdd,
    BookPATCHWithRels,
    TagAdd,
    GenresBooksAdd,
    BookPATCH,
    BookEditRenderStatus,
)
from src.schemas.books_authors import BookAuthorAdd
from src.exceptions.base import ForeignKeyException, ObjectNotFoundException
from src.exceptions.books import (
    AuthorNotFoundException,
    BookAlreadyPublicatedException,
    BookNotExistsOrYouNotOwnerException,
    BookNotFoundException,
    ContentAlreadyExistsException,
    ContentNotFoundException,
    CoverAlreadyExistsException,
    CoverNotFoundException,
    GenreNotFoundException,
)
from src.tasks.tasks import change_content, delete_book_images, render_book
from validation.files import FileValidator


class AuthorsService(BaseService):
    async def add_book(self, user_id: int, data: BookAddWithAuthorsTagsGenres):
        if user_id not in data.authors:
            data.authors.append(user_id)
        book = await self.db.books.add(BookAdd(**data.model_dump()))
        data_to_add_m2m = [
            BookAuthorAdd(book_id=book.book_id, author_id=author_id)
            for author_id in set(data.authors) or []
        ]
        data_to_tags_m2m = [
            TagAdd(book_id=book.book_id, title_tag=title)
            for title in set(data.tags) or []
        ]
        data_to_genres_m2m = [
            GenresBooksAdd(book_id=book.book_id, genre_id=gen_id)
            for gen_id in set(data.genres) or []
        ]
        try:
            await self.db.books_authors.add_bulk(data_to_add_m2m)
        except ForeignKeyException as ex:
            raise AuthorNotFoundException from ex
        try:
            if data_to_tags_m2m:
                await self.db.tags.add_bulk(data_to_tags_m2m)
        except ForeignKeyException as ex:
            raise BookNotFoundException from ex
        try:
            if data_to_genres_m2m:
                await self.db.books_genres.add_bulk(data_to_genres_m2m)
        except ForeignKeyException as ex:
            raise GenreNotFoundException from ex
        await self.db.commit()
        return book

    async def edit_book(
        self, book_id: int, user_id: int, user_role: str, data: BookPATCHWithRels
    ):
        try:
            await self.db.books.get_one(book_id=book_id)
        except BookNotFoundException:
            raise
        if user_role not in ["ADMIN", "GENERAL_ADMIN"]:
            try:
                await AuthService(db=self.db).verify_user_owns_book(
                    user_id=user_id, book_id=book_id
                )  # Проверяем, владеет ли пользователь этой книгой
            except BookNotExistsOrYouNotOwnerException:
                raise
        book_patch_data = BookPATCH(
            **data.model_dump(exclude_unset=True)
        )  # Создаем pydantic-схему для будущего изменения данных

        # --- Изменение жанров и тегов ---
        genres = await self.db.books_genres.get_filtered(
            book_id=book_id
        )  # Получаем все жанры книги
        tags = await self.db.tags.get_filtered(book_id=book_id)
        genres_ids_in_db = [genre.genre_id for genre in genres]
        tags_titles_in_db = [tag.title_tag for tag in tags]
        # Вычисление нужных и НЕ нужных нам жанров
        new_genres = data.genres or set()
        same_els_genres = set(genres_ids_in_db) & set(new_genres)
        genres_to_add = set(new_genres) - same_els_genres
        genres_to_delete = set(genres_ids_in_db) - same_els_genres
        # Вычисление нужных и НЕ нужных нам тегов
        new_tags = data.tags or set()
        same_els_tags = set(tags_titles_in_db) & set(new_tags)
        tags_to_add = set(new_tags) - same_els_tags
        tags_to_delete = set(tags_titles_in_db) - same_els_tags

        data_to_add_genres = [
            GenresBooksAdd(genre_id=gen_book_id, book_id=book_id)
            for gen_book_id in genres_to_add
        ]

        data_to_add_tags = [
            TagAdd(title_tag=tag_book_title, book_id=book_id)
            for tag_book_title in tags_to_add
        ]

        # --- Изменение жанров внутри базы данных ---
        if genres_to_delete:
            await self.db.books_genres.delete_bulk_by_ids(
                genres_to_delete, book_id=book_id
            )
        if genres_to_add:
            try:
                await self.db.books_genres.add_bulk(data_to_add_genres)
            except ForeignKeyException as ex:
                raise GenreNotFoundException from ex
        if tags_to_delete:
            await self.db.tags.delete(
                BooksTagsORM.title_tag.in_(tags_to_delete), book_id=book_id
            )
        if tags_to_add:
            try:
                await self.db.tags.add_bulk(data_to_add_tags)
            except ForeignKeyException as ex:
                raise GenreNotFoundException from ex
        if book_patch_data.model_dump(exclude_unset=True):
            await self.db.books.edit(
                data=book_patch_data, is_patch=True, book_id=book_id
            )
        await self.db.commit()

    async def delete_book(self, should_check_owner: bool, book_id: int, user_id: int):
        if should_check_owner:
            await AuthService(db=self.db).verify_user_owns_book(
                user_id=user_id, book_id=book_id
            )
        try:
            book = await self.db.books.get_one(book_id=book_id)
        except BookNotFoundException:
            raise
        delete_book_images.delay(book_id)
        if book.is_rendered:
            await self.s3.books.delete_by_path(f"books/{book_id}/book.pdf")
        if book.cover_link:
            await self.s3.books.delete_by_path(f"books/{book_id}/preview.png")
        await self.db.pages.delete(book_id=book_id)
        await self.db.books.delete(book_id=book_id)
        await self.db.commit()

    async def get_my_books(self, author_id: int):
        return await self.db.users.get_books_by_user(user_id=author_id)

    async def add_cover(
        self, should_check_owner: bool, book_id: int, user_id: int, file: UploadFile
    ):
        if should_check_owner:
            await AuthService(db=self.db).verify_user_owns_book(
                user_id=user_id, book_id=book_id
            )
        try:
            FileValidator.check_expansion_images(file_name=file.filename)
            await FileValidator.validate_cover(file_img=file)
        except WrongCoverResolutionException:
            raise
        except WrongFileExpensionException:
            raise
        book = await self.db.books.get_one(book_id=book_id)
        if book.cover_link is not None:
            raise CoverAlreadyExistsException
        cover_link = await self.s3.books.save_cover(file=file, book_id=book_id)
        await self.db.books.edit(
            is_patch=True,
            data=BookPATCHOnPublication(cover_link=cover_link),
            book_id=book_id,
        )
        await self.db.commit()

    async def put_cover(
        self, should_check_owner: bool, book_id: int, user_id: int, file: UploadFile
    ):
        if should_check_owner:
            await AuthService(db=self.db).verify_user_owns_book(
                user_id=user_id, book_id=book_id
            )
        try:
            FileValidator.check_expansion_images(file_name=file.filename)
            await FileValidator.validate_cover(file_img=file)
        except WrongCoverResolutionException as ex:
            raise WrongCoverResolutionException from ex
        except WrongFileExpensionException as ex:
            raise WrongFileExpensionException from ex
        book = await self.db.books.get_one(book_id=book_id)
        if not book.cover_link:
            raise CoverNotFoundException
        await self.s3.books.save_cover(file=file, book_id=book_id)
        await self.db.books.edit(
            is_patch=True,
            data=BookPATCHOnPublication(cover_link=f"books/{book_id}/preview.png"),
            book_id=book_id,
        )
        await self.db.commit()

    async def add_all_content(
        self, should_check_owner, user_id: int, book_id: int, file: UploadFile
    ):
        if should_check_owner:
            await AuthService(db=self.db).verify_user_owns_book(
                user_id=user_id, book_id=book_id
            )
        try:
            FileValidator.check_expansion_books(file_name=file.filename)
        except WrongFileExpensionException as ex:
            raise WrongFileExpensionException from ex
        try:
            book = await self.db.books.get_one(book_id=book_id)
        except ObjectNotFoundException as ex:
            raise BookNotFoundException from ex
        if book.is_rendered:
            raise ContentAlreadyExistsException
        await self.s3.books.save_content(book_id, file=file)
        render_book.delay(book_id)

    async def edit_content(
        self, should_check_owner, user_id: int, book_id: int, file: UploadFile
    ):
        if should_check_owner:
            await AuthService(db=self.db).verify_user_owns_book(
                user_id=user_id, book_id=book_id
            )
        try:
            FileValidator.check_expansion_books(file_name=file.filename)
        except WrongFileExpensionException as ex:
            raise WrongFileExpensionException from ex
        if not await self.s3.books.check_file_by_path(f"books/{book_id}/book.pdf"):
            raise ContentNotFoundException
        await self.s3.books.save_content(book_id=book_id, file=file)
        await self.db.pages.delete(book_id=book_id)
        change_content.delay(book_id)
        await self.db.commit()

    async def publicate_book(
        self,
        book_id,
        user_id,
        should_check_owner,
    ):
        try:
            if should_check_owner:
                book = await AuthService(db=self.db).verify_user_owns_book(
                    user_id=user_id, book_id=book_id
                )
            else:
                book = await self.db.books.get_one(book_id=book_id)
        except BookNotFoundException:
            raise
        if (not book.is_rendered) or (book.total_pages is None):
            raise ContentNotFoundException
        if book.cover_link is None:
            raise CoverNotFoundException
        if book.is_publicated:
            raise BookAlreadyPublicatedException
        data_to_update = BookPATCH(is_publicated=True)
        updated_data = await self.db.books.edit(
            data=data_to_update, is_patch=True, book_id=book_id
        )
        await self.db.commit()
        return updated_data
