from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_PREFIX: str = "/api/v1"

    MONGODB_USER: str
    MONGODB_PASSWORD: str
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_NAME: str
    EXTERNAL_HOST: str
    SFTP_PORT: int
    SFTP_USER: str
    SFTP_PASSWORD: str
    SFTP_PATH: str

    class Config:
        env_file = ".env"


settings = Settings()
