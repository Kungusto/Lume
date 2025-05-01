from passlib.context import CryptContext


class AuthService : 
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    