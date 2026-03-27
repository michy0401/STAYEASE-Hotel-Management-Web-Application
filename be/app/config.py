from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    token_expire_minutes: int = 60
    algorithm: str = "HS256"

    class Config:
        case_sensitive = False

settings = Settings()