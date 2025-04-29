from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])

@router.post("/register")
async def registrate_users(data, db) : 
    ...