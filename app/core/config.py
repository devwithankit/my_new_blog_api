from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int   # ✅ ADD THIS

    OTP_CODE: str
    OTP_EXPIRE_MINUTES: int

    ACCESS_KEY: str
    SECRET_KEY_API: str

    class Config:
        env_file = ".env" 

settings = Settings()