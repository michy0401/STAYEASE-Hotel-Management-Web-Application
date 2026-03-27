from sqlalchemy.orm import Session
from app.models.room import Room

def get_all(db: Session) -> list[Room]:
    return db.query(Room).all()

def get_available(db: Session) -> list[Room]:
    return db.query(Room).filter(Room.status == "available").all()

def get_by_id(db: Session, room_id: int) -> Room | None:
    return db.query(Room).filter(Room.id == room_id).first()

def create(db: Session, data_dict: dict) -> Room:
    db_room = Room(**data_dict)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def update(db: Session, room: Room, data_dict: dict) -> Room:
    for key, value in data_dict.items():
        if value is not None:
            setattr(room, key, value) # Actualiza solo los campos que no sean None
    db.commit()
    db.refresh(room)
    return room

def update_status(db: Session, room: Room, new_status: str) -> Room:
    room.status = new_status
    db.commit()
    db.refresh(room)
    return room