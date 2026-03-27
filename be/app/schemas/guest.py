from pydantic import BaseModel, EmailStr
from typing import Optional

class GuestCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    document_id: Optional[str] = None

class GuestOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    document_id: Optional[str] = None

    class Config:
        from_attributes = True