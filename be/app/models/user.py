from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False) 
    full_name = Column(String(100), nullable=True)
    role = Column(Enum("staff", "manager", name="user_roles"), nullable=False, default="staff")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())