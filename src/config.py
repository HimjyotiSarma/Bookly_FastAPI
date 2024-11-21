from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ROOT_ROUTE: str
    DATABASE_URL: str
    JWT_PRIVATE: str
    JWT_ALGORITHM: str
    REDIS_HOST: str
    REDIS_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DANGEROUS_TOKEN: str
    DANGEROUS_MAX_AGE: int
    DOMAIN: str
    VERSION: str

    class Config:
        env_file = ".env"


settings = Settings()
