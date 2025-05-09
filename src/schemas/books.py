from datetime import date
from pydantic import BaseModel, EmailStr
from src.enums.users import AllUsersRolesEnum
from src.enums.books import LanguagesEnum
from src.schemas.users import User, UserPublicData

# Для отрисовки картинок на сайте. 
class SourceImage(BaseModel) :
    file_id: int
    book_id: int
    src: str

# Добавление путей для файлов
class SourceImageAdd(BaseModel) :
    book_id: int
    src: str

class Page(BaseModel) : 
    book_id: int
    page_number: int
    text: str
    images: list[SourceImage] = []


# Теги
class Tag(BaseModel) :
    id: int
    book_id: int
    title_tag: str

class TagAdd(BaseModel) :
    book_id: int
    title_tag: str

class TagEdit(BaseModel) :
    title_tag: str

# Жанры
class Genre(BaseModel) :
    genre_id: int
    title: str

class GenreAdd(BaseModel) :
    title: str

class GenreEdit(GenreAdd) : ...

# M2M Жанров и книг
class GenresBook(BaseModel) :
    id: int
    genre_id: int
    book_id: int

class GenresBooksAdd(BaseModel) : 
    genre_id: int
    book_id: int

# Книги
class BookAuthors(BaseModel) :
    authors: list[int]
    book_id: int

class BookAdd(BaseModel) : 
    title: str
    age_limit: int
    description: str | None
    language: LanguagesEnum  

class BookAddWithAuthorsTagsGenres(BookAdd) : 
    authors: list[int] = []
    genres: list[int] 
    tags: list[str]     

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

class BookPATCHWithRels(BaseModel):
    title: str | None = None
    age_limit: int | None = None
    description: str | None = None
    genres: list[int] | None = None

class BookPATCH(BaseModel) :
    title: str | None = None
    age_limit: int | None = None
    description: str | None = None

class BookPUT(BaseModel):
    title: str = None
    age_limit: int = None
    description: str | None = None
    
class BookWithAuthors(Book) :
    authors: list[User] 

class BookPATCHOnPublication(BaseModel) :
    is_rendered: bool | None = False
    cover_link: str | None = None

class BookData(Book) :
    pages_count: int

class BookDataWithRels(Book) :
    authors: list[UserPublicData] # список авторов
    tags: list[Tag] # список тегов
    genres: list[Genre] # список жанров

class BookDataWithTagRel(BookData) :
    tags: list[int] # список тегов

class BookDataWithGenresRel(BookData) :
    genres: list[int] # список жанров


class FullDataAboutBook(BookData) :
    count_readers: int

# Авторы
class UserWithBooks(BaseModel) :
    user_id: int
    role: AllUsersRolesEnum
    email: EmailStr
    name: str
    surname: str
    nickname: str
    last_activity: date
    registation_date: date
    books: list[Book]
