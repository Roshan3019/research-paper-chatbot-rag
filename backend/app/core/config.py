from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Research Paper ChatBot API"
    DEBUG: bool = False

    DATABASE_URL: str
    SECRET_KEY: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CHROMA_PERSIST_DIR: str = "../chroma_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()