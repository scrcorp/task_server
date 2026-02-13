from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "TaskServerAPI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Supabase (DB only — auth is handled by custom JWT)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "TaskManager"

    # Email verification (6-digit OTP)
    EMAIL_VERIFY_CODE_EXPIRE_MINUTES: int = 10
    APP_BASE_URL: str = "http://localhost:8000"

    # CORS
    CORS_ORIGINS: str = "*"  # comma-separated, e.g. "http://localhost:3000,https://myapp.com"

    # Storage
    STORAGE_BUCKET_NAME: str = "task-assets"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_EXTENSIONS: str = "jpg,jpeg,png,gif,webp,pdf,doc,docx,xls,xlsx,ppt,pptx,txt,csv,zip"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
