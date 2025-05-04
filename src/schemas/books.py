from datetime import date
from pydantic import BaseModel
from src.enums.books import LanguagesEnum

# Для отрисовки картинок на сайте. 
class SourceImage(BaseModel) :
    id: int
    src: str

class Page(BaseModel) : 
    book_id: int
    page_number: int
    text: str
    images: list[SourceImage] = []

class BookAuthors(BaseModel) :
    authors: list[int]
    book_id: int

class BookAdd(BaseModel) : 
    title: str
    age_limit: int
    description: str | None
    language: LanguagesEnum  

class BookAddWithAuthors(BookAdd) : 
    authors: list[int] = []

class Book(BaseModel) :
    book_id: int
    title: str
    age_limit: int
    description: str | None
    language: LanguagesEnum
    book_id: int
    date_publicated: date
    is_rendered: bool = False
    cover_link: str | None = None

class BookPATCHOnPublication(BaseModel) :
    is_rendered: bool | None = False
    cover_link: str | None = None

class BookData(Book) :
    pages_count: int

class BookDataWithRels(BookData) :
    tags: list[int] # список тегов
    genres: list[int] # список жанров

class BookDataWithTagRel(BookData) :
    tags: list[int] # список тегов

class BookDataWithGenresRel(BookData) :
    genres: list[int] # список жанров


class FullDataAboutBook(BookData) :
    count_readers: int
    rate: int

class Tag(BaseModel) :
    id: int
    book_id: int
    title_tag: str

class TagAdd(BaseModel) :
    book_id: str
    title_tag: str

class TagEdit(BaseModel) :
    title_tag: str

class Genre(BaseModel) :
    genre_id: int
    title: str

class GenreAdd(BaseModel) :
    title: str

class GenreEdit(GenreAdd) : ...