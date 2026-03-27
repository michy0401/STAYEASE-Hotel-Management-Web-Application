from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.room import RoomCreate, RoomUpdate, RoomOut
from app.services import room_service
from app.routers.deps import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/rooms", tags=["Rooms"])

class StatusUpdate(BaseModel):
    status: str

@router.get("/", response_model=list[RoomOut])
def get_all_rooms(db: Session = Depends(get_db)):
    return room_service.get_rooms(db)

@router.get("/available", response_model=list[RoomOut])
def get_available_rooms(db: Session = Depends(get_db)):
    return room_service.get_available_rooms(db)

@router.post("/", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def add_room(data: RoomCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return room_service.add_room(db, data)

@router.patch("/{room_id}", response_model=RoomOut)
def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    updated_room = room_service.update_room(db, room_id, data)
    if not updated_room:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    return updated_room

@router.patch("/{room_id}/status", response_model=RoomOut)
def update_room_status(room_id: int, data: StatusUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    updated_room = room_service.update_room_status(db, room_id, data.status)
    if not updated_room:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Habitación no encontrada o estado inválido")
    return updated_room