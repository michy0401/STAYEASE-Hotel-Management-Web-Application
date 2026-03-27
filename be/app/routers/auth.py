from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserOut, LoginRequest
from app.schemas.token import Token
from app.services import auth_service
from app.repositories import user_repo

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if user_repo.get_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    return auth_service.register(db, data)

@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    token = auth_service.login(db, data.username, data.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    return {"access_token": token, "token_type": "bearer"}