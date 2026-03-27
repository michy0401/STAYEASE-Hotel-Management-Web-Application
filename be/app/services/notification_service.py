import asyncio
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.repositories import notification_repo
from app.models.notification import Notification

# Aquí guardamos a todos los empleados conectados actualmente
_connections: dict[int, WebSocket] = {}

def register_ws(user_id: int, websocket: WebSocket):
    _connections[user_id] = websocket

def unregister_ws(user_id: int):
    if user_id in _connections:
        del _connections[user_id]

async def push(user_id: int, payload_dict: dict):
    """Envía un mensaje a un solo usuario (si está conectado)"""
    if user_id in _connections:
        socket = _connections[user_id]
        try:
            await socket.send_json(payload_dict)
        except Exception:
            pass # Si falla, simplemente lo ignoramos (ej. se desconectó de golpe)

async def broadcast(payload_dict: dict):
    """Envía un mensaje a TODOS los usuarios conectados (Fan-out)"""
    for socket in list(_connections.values()):
        try:
            await socket.send_json(payload_dict)
        except Exception:
            pass

def send(db: Session, user_id: int, title: str, message: str, ntype: str, related_reservation_id: int | None = None):
    """Guarda la notificación en la base de datos y la empuja por WebSocket"""
    # 1. Siempre la guardamos en la base de datos (Durable)
    notif = notification_repo.create(db, user_id, title, message, ntype, related_reservation_id)
    
    # 2. Intentamos enviarla en tiempo real
    payload = {
        "type": ntype,
        "title": title,
        "message": message,
        "notification_id": notif.id
    }
    try:
        # Ejecutamos el push sin detener el resto del programa
        asyncio.ensure_future(push(user_id, payload))
    except RuntimeError:
        pass

def get_user_notifications(db: Session, user_id: int) -> list[Notification]:
    return notification_repo.get_for_user(db, user_id)