from dataclasses import dataclass
from decouple import config

@dataclass
class Settings:
    # Database
    MONGODB_URL: str = config("MONGODB_URL")
    # Auth
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=15, cast=int)
    # AWS
    AWS_ACCESS_KEY: str = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY: str = config("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = config("AWS_REGION")
    S3_BUCKET: str = config("S3_BUCKET_NAME")
    ENVIRONMENT: str = config("ENVIRONMENT", default="development")

settings = Settings()

