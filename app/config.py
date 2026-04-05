from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings.
    Loads OPENAI_API_KEY from environment variables or .env file.
    """
    OPENAI_API_KEY: Optional[str] = None
    
    # Pydantic V2 configuration
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
