from sqlalchemy.orm import Session
from app.repositories import room_repo
from app.schemas.room import RoomCreate, RoomUpdate
from app.models.room import Room

def get_rooms(db: Session) -> list[Room]:
    return room_repo.get_all(db)

def get_available_rooms(db: Session) -> list[Room]:
    return room_repo.get_available(db)

def add_room(db: Session, data: RoomCreate) -> Room:
    return room_repo.create(db, data.model_dump())

def update_room(db: Session, room_id: int, data: RoomUpdate) -> Room | None:
    room = room_repo.get_by_id(db, room_id)
    if not room:
        return None
    return room_repo.update(db, room, data.model_dump(exclude_unset=True))

def update_room_status(db: Session, room_id: int, new_status: str) -> Room | None:
    room = room_repo.get_by_id(db, room_id)
    valid_statuses = ["available", "occupied", "cleaning", "maintenance"]
    if not room or new_status not in valid_statuses:
        return None
    return room_repo.update_status(db, room, new_status)