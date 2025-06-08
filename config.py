from decouple import config

class Settings:
    MONGODB_URL: str = config("MONGODB_URL")
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7, cast=int)
    ENVIRONMENT: str = config("ENVIRONMENT", default="development")
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = config("GOOGLE_CLIENT_ID", default="")
    GOOGLE_CLIENT_SECRET: str = config("GOOGLE_CLIENT_SECRET", default="")
    GOOGLE_REDIRECT_URI: str = config("GOOGLE_REDIRECT_URI", default="http://localhost:8000/api/v1/auth/google/callback")

    # Google Gemini AI settings
    GEMINI_API_KEY: str = config("GEMINI_API_KEY")
    GEMINI_MODEL: str = config("GEMINI_MODEL", default="gemini-1.5-flash")
    GEMINI_MAX_OUTPUT_TOKENS: int = config("GEMINI_MAX_OUTPUT_TOKENS", default=512, cast=int)
    GEMINI_TEMPERATURE: float = config("GEMINI_TEMPERATURE", default=0.3, cast=float)

settings = Settings()

