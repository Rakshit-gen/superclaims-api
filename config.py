from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GROQ_API_KEY: str
    LLM_MODEL: str = "llama-3.1-70b-versatile"
    MAX_FILE_SIZE_MB: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()