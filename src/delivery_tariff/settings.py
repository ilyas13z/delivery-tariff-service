from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str
    port: int

    database_url: str
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str

    broker_celery_url: str
    backend_celery_url: str
    timezone_celery: str = "UTC"

    session_cookie: str

    redis_database_host: str
    redis_database_port: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

        case_sensitive = False

        extra = "ignore"
