from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central application configuration.
    All values can be overridden via environment variables or a .env file,
    so secrets never live in source control.
    """
    PROJECT_NAME: str = "LibTrack"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./libtrack.db"

    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    LOAN_PERIOD_DAYS: int = 14
    FINE_PER_DAY: float = 0.50

    class Config:
        env_file = ".env"


settings = Settings()
