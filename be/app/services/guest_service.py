from sqlalchemy.orm import Session
from app.repositories import guest_repo
from app.schemas.guest import GuestCreate
from app.models.guest import Guest

def get_guests(db: Session) -> list[Guest]:
    return guest_repo.get_all(db)

def get_guest(db: Session, guest_id: int) -> Guest | None:
    return guest_repo.get_by_id(db, guest_id)

def add_guest(db: Session, data: GuestCreate) -> Guest | None:
    # Regla de negocio: El email debe ser único
    existing = guest_repo.get_by_email(db, data.email)
    if existing:
        return None
    return guest_repo.create(db, data.model_dump())