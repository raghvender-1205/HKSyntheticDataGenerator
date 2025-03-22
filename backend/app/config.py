from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str = ""
    gemini_api_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./data/synthetic_data.db"
    environment: str = "development"
    debug: bool = True

    model_config = SettingsConfigDict(env_file=".env")
    
settings = Settings()