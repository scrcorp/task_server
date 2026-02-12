from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TaskServerAPI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
