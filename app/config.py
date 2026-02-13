# Configuration
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    anthropic_api_key: str = ""
    
    # LLM Config
    default_model: str = "gpt-4-turbo"
    default_temperature: float = 0.7
    max_tokens: int = 2000
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Database
    database_url: str = "sqlite:///./app.db"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()