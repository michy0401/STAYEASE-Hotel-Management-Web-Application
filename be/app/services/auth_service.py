import logging 
logging.getLogger('passlib').setLevel(logging.ERROR) 

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.repositories import user_repo
from app.schemas.user import UserCreate
from app.schemas.token import TokenData
from app.models.user import User
from app.config import settings

# Configuramos la encriptación bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.token_expire_minutes)
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    user_id: str = payload.get("sub")
    if user_id is None:
        raise JWTError()
    return TokenData(user_id=int(user_id))

def register(db: Session, data: UserCreate) -> User:
    hashed_pw = hash_password(data.password)
    return user_repo.create(db, data.username, data.email, hashed_pw, data.full_name, "staff")

def login(db: Session, username: str, password: str) -> str | None:
    user = user_repo.get_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return create_access_token(user.id)