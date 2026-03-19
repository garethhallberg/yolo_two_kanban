"""
Application settings configuration using Pydantic Settings.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    """
    # Application
    app_name: str = "Kanban Backend"
    environment: str = "development"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Database
    database_url: str = "sqlite:///./kanban.db"
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Integration
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "openai/gpt-oss-120b"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Create settings instance
settings = Settings()