from datetime import date
from pydantic import BaseModel, EmailStr

class User(BaseModel) : 
    user_id: int
    role_id: int
    email: str = EmailStr
    name: str
    surname: str
    nickname: str
    phone: int
    last_activity: date
    hashed_password: str
    registation_date: date