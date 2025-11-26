"""
Конфигурация приложения
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения из environment variables"""
    
    # LLM Configuration
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    MISTRAL_API_KEY: Optional[str] = None
    
    # Router & Assistant Models (optional overrides)
    LLM_ROUTER_MODEL: Optional[str] = None
    LLM_ASSISTANT_MODEL: Optional[str] = None
    
    # Fallback Configuration
    LLM_FALLBACK_PROVIDER: Optional[str] = None
    
    # App Settings
    APP_NAME: str = "ForteBank BA Assistant"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton
settings = Settings()