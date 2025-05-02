from fastapi import APIRouter, UploadFile
from src.api.dependencies import S3Dep, DBDep
from src.schemas.books import BookAdd

router = APIRouter(prefix="/books", tags=["Книги"])

@router.post("/book")
async def add_book(data: BookAdd, db: DBDep) : 
    book = await db.books.add(data)
    await db.commit()
    return {"status": "OK", "data": book}

@router.post("/cover")
async def add_cover(file: UploadFile) :
    ...

@router.post("/content")
async def add_all_content(file: UploadFile) : 
    ...

