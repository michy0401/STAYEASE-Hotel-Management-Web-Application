import asyncio
from sqlalchemy.orm import Session
from app.repositories import reservation_repo, room_repo, guest_repo
from app.schemas.reservation import ReservationCreate
from app.models.reservation import Reservation
from app.services import notification_service

def create_reservation(db: Session, staff_id: int, data: ReservationCreate) -> Reservation | None:
    # 1. Validar la habitación
    room = room_repo.get_by_id(db, data.room_id)
    if not room or room.status != "available":
        return None
        
    # 2. Validar el huésped
    guest = guest_repo.get_by_id(db, data.guest_id)
    if not guest:
        return None

    # 3. Crear la reserva (fijando el precio actual de la habitación)
    reservation = reservation_repo.create(
        db, room.id, guest.id, staff_id, 
        data.check_in_date, data.check_out_date, 
        room.price_per_night, data.notes
    )

    # 4. Actualizar la habitación a ocupada
    room_repo.update_status(db, room, "occupied")

    # 5. Notificar al empleado
    notification_service.send(
        db, staff_id, "Reserva Creada", 
        f"Reserva confirmada para {guest.full_name} en habitación {room.room_number}", 
        "reservation_created", reservation.id
    )

    return reservation

def get_my_reservations(db: Session, staff_id: int) -> list[Reservation]:
    return reservation_repo.get_by_staff(db, staff_id)

def get_all_reservations(db: Session) -> list[Reservation]:
    return reservation_repo.get_all(db)

def update_reservation_status(db: Session, reservation_id: int, requesting_user_id: int, new_status: str) -> Reservation | None:
    reservation = reservation_repo.get_by_id(db, reservation_id)
    if not reservation:
        return None

    current_status = reservation.status
    
    # Reglas de transición válidas
    if current_status == "confirmed" and new_status not in ["checked_in", "cancelled"]:
        return None
    if current_status == "checked_in" and new_status != "checked_out":
        return None
    if current_status in ["checked_out", "cancelled"]: # Ya no se pueden mover
        return None

    # Actualizar estado de la reserva
    reservation = reservation_repo.update_status(db, reservation, new_status)
    room = room_repo.get_by_id(db, reservation.room_id)

    # Lógica derivada según el nuevo estado
    if new_status == "checked_in":
        room_repo.update_status(db, room, "occupied")
        notification_service.send(db, requesting_user_id, "Check-in Exitoso", f"El huésped ha ingresado a la habitación {room.room_number}", "guest_checked_in", reservation.id)
        
    elif new_status == "checked_out":
        room_repo.update_status(db, room, "cleaning")
        
        # EL MOMENTO MÁGICO: Avisamos a TODOS los empleados que la habitación necesita limpieza
        broadcast_payload = {
            "type": "room_status_update",
            "room_id": room.id,
            "room_number": room.room_number,
            "new_status": "cleaning"
        }
        asyncio.ensure_future(notification_service.broadcast(broadcast_payload))
        
        notification_service.send(db, requesting_user_id, "Check-out Exitoso", f"La habitación {room.room_number} necesita limpieza", "guest_checked_out", reservation.id)
        
    elif new_status == "cancelled":
        room_repo.update_status(db, room, "available")
        notification_service.send(db, requesting_user_id, "Reserva Cancelada", f"La habitación {room.room_number} vuelve a estar disponible", "reservation_cancelled", reservation.id)

    return reservation