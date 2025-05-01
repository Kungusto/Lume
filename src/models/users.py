from datetime import date
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, String, Integer
from src.database import Base

class UsersOrm(Base) : 
    __tablename__ = "Users"

    user_id: Mapped[int] = mapped_column(primary_key=True)    
    role_id: Mapped[int] = ForeignKey("Roles.role_id")
    email: Mapped[str] = mapped_column(String(254), unique=True)
    name: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str]
    nickname: Mapped[str] = mapped_column(String(30), unique=True)
    phone: Mapped[int] = mapped_column(Integer(), unique=True)
    last_activity: Mapped[date]
    hashed_password: Mapped[str]
    registation_date: Mapped[date]
    