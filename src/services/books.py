from src.models.books import BooksTagsORM
from src.services.base import BaseService
from src.services.auth import AuthService
from src.schemas.books import BookAddWithAuthorsTagsGenres
from src.schemas.books import (
    BookAdd,
    BookAddWithAuthorsTagsGenres,
    BookPATCHWithRels,
    BookPATCHOnPublication,
    TagAdd,
    GenresBooksAdd,
    BookPATCH,
)
from src.schemas.books_authors import BookAuthorAdd
from src.exceptions.base import ForeignKeyException
from src.exceptions.books import (
    AuthorNotFoundException,
    BookNotExistsOrYouNotOwnerException,
    BookNotFoundException,
    GenreNotFoundException,
)
from src.tasks.tasks import delete_book_images


class BookService(BaseService):
    async def add_book(self, user_id: int, data: BookAddWithAuthorsTagsGenres):
        if user_id not in data.authors:
            data.authors.append(user_id)
        book = await self.self.db.books.add(BookAdd(**data.model_dump()))
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
            await self.self.db.books_authors.add_bulk(data_to_add_m2m)
        except ForeignKeyException as ex:
            raise AuthorNotFoundException from ex
        try:
            if data_to_tags_m2m:
                await self.self.db.tags.add_bulk(data_to_tags_m2m)
        except ForeignKeyException as ex:
            raise BookNotFoundException from ex
        try:
            if data_to_genres_m2m:
                await self.self.db.books_genres.add_bulk(data_to_genres_m2m)
        except ForeignKeyException as ex:
            raise GenreNotFoundException from ex
        await self.self.db.commit()
        return book

    async def edit_book(
        self, book_id: int, user_id: int, user_role: str, data: BookPATCHWithRels
    ):
        try:
            await self.db.books.get_one(book_id=book_id)
        except BookNotFoundException as ex:
            raise
        if user_role not in ["ADMIN", "GENERAL_ADMIN"]:
            try:
                await AuthService(db=self.db).verify_user_owns_book(
                    user_id=user_id, book_id=book_id
                )  # Проверяем, владеет ли пользователь этой книгой
            except BookNotExistsOrYouNotOwnerException as ex:
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
