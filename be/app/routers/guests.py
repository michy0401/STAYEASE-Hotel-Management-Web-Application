from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.guest import GuestCreate, GuestOut
from app.services import guest_service
from app.routers.deps import get_current_user

router = APIRouter(prefix="/guests", tags=["Guests"])

@router.get("/", response_model=list[GuestOut])
def get_all_guests(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return guest_service.get_guests(db)

@router.get("/{guest_id}", response_model=GuestOut)
def get_guest(guest_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    guest = guest_service.get_guest(db, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Huésped no encontrado")
    return guest

@router.post("/", response_model=GuestOut, status_code=status.HTTP_201_CREATED)
def add_guest(data: GuestCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    guest = guest_service.add_guest(db, data)
    if not guest:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un huésped con ese email")
    return guest