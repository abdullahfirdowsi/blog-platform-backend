from dataclasses import dataclass, field
from typing import List
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

    # AI Summary
    GEMINI_API_KEY: str = config("GEMINI_API_KEY")
    GEMINI_MODEL: str = config("GEMINI_MODEL", default="gemini-1.5-flash")
    GEMINI_TEMPERATURE: float = config("GEMINI_TEMPERATURE", default=0.7, cast=float)
    GEMINI_TOP_P: float = config("GEMINI_TOP_P", default=0.8, cast=float)
    GEMINI_TOP_K: int = config("GEMINI_TOP_K", default=40, cast=int)
    GEMINI_MAX_TOKENS: int = config("GEMINI_MAX_TOKENS", default=2048, cast=int)

    # Environment
    ENVIRONMENT: str = config("ENVIRONMENT", default="development")

    # Email Configuration
    SMTP_HOST: str = config("SMTP_HOST", default="smtp.gmail.com")
    SMTP_PORT: int = config("SMTP_PORT", default=587, cast=int)
    SMTP_USERNAME: str = config("SMTP_USERNAME")
    SMTP_PASSWORD: str = config("SMTP_PASSWORD")
    EMAIL_FROM_NAME: str = config("EMAIL_FROM_NAME", default="Blog Platform")
    EMAIL_FROM_ADDRESS: str = config("EMAIL_FROM_ADDRESS")
    FRONTEND_URL: str = config("FRONTEND_URL")
    RESET_TOKEN_EXPIRE_MINUTES: int = config("RESET_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = config("EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES", default=1440, cast=int)  # 24 hours

    # CORS Configuration
    CORS_ORIGINS: List[str] = field(default_factory=lambda: config("CORS_ORIGINS", default="http://localhost:4200,http://127.0.0.1:4200,https://blogplatformapplicationilink.netlify.app", cast=lambda v: [s.strip() for s in v.split(',')]))


settings = Settings()
