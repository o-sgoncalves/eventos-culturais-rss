from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    cache_ttl: int = 21600  # 6 horas em segundos
    cache_dir: str = "/app/cache"
    log_level: str = "INFO"

    instagram_accounts: List[str] = [
        "espacocultural_gyn",
        "casadoponte",
        "teatro_goiania",
        "centro_cultural_ufg",
        "sesc_goias",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
