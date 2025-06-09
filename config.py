from dataclasses import dataclass
from decouple import config


@dataclass
class Settings:
    # Database
    MONGODB_URL: str = config("MONGODB_URL", default="mongodb://localhost:27017/blog_platform")
    # Auth
    SECRET_KEY: str = config("SECRET_KEY", default="your-secret-key-here")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=15, cast=int)
    # AWS
    AWS_ACCESS_KEY: str = config("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_KEY: str = config("AWS_SECRET_ACCESS_KEY", default="")
    AWS_REGION: str = config("AWS_REGION", default="us-east-1")
    S3_BUCKET: str = config("S3_BUCKET_NAME", default="")
    ENVIRONMENT: str = config("ENVIRONMENT", default="development")

settings = Settings()

