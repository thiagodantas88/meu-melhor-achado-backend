from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    FRONTEND_URL: str = "https://meumelhorachado.com.br"
    AMAZON_TAG: str = "meumelhoracha-20"
    MAGALU_STORE: str = "magazinemeumelhorachado"
    AUTO_SEED_ON_START: bool = True
    SCRAPER_MORNING_HOUR: int = 6
    SCRAPER_MORNING_MINUTE: int = 0
    SCRAPER_EVENING_HOUR: int = 15
    SCRAPER_EVENING_MINUTE: int = 30
    SCRAPER_ENABLED: bool = True
    SCRAPER_MAX_DEALS_PER_RUN: int = 30
    SCRAPER_FALLBACK_ENABLED: bool = True
    LOG_SCRAPER_RUNS: bool = True
    MOBILIA_USER: str = "thiagodantas@outlook.com"
    MOBILIA_PASSWORD: str = "0987654321"

    class Config:
        env_file = ".env"

settings = Settings()
