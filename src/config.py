from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ROOT_ROUTE: str
    DATABASE_URL: str
    JWT_PRIVATE: str
    JWT_ALGORITHM: str
    REDIS_HOST: str
    REDIS_PORT: int


    class Config:
        env_file = ".env"

settings = Settings()