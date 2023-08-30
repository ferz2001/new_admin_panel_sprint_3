from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_OPTIONS: str = '-c search_path=content'
    ES_URL: str
    POLING_DATA_INTERVAL: int = 5

    class Config:
        env_file = '.env'