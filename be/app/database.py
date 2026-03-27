from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

# Crea el motor de conexión a la base de datos
engine = create_engine(settings.database_url, pool_pre_ping=True)

# Crea la fábrica de sesiones (como "ventanillas" de atención a la base de datos)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para nuestros modelos
class Base(DeclarativeBase):
    pass

# Generador de sesiones para usar en nuestras rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()