from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://goiania:secret@db:5432/goiania_cultural"
    redis_url: str = "redis://redis:6379"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    rss_service_url: str = "http://rss-scraper:8000"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost", "http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
