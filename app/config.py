from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    FRONTEND_URL: str = "https://meumelhorachado.com.br"
    AMAZON_TAG: str = "meumelhoracha-20"
    MAGALU_STORE: str = "https://www.magazinevoce.com.br/magazinemeumelhorachado"
    AUTO_SEED_ON_START: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
