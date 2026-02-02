from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Smart Financial Coach"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 12
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # Plaid
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    PLAID_ENV: str = "sandbox"
    PLAID_PRODUCTS: list = ["transactions", "auth", "identity"]
    PLAID_COUNTRY_CODES: list = ["US"]
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4"
    
    # Email
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@fincoach.app"
    
    # Feature Flags
    ENABLE_MFA: bool = True
    ENABLE_GAMIFICATION: bool = True
    MAX_INSIGHTS_PER_DAY: int = 2
    
    class Config:
        # Look for .env file in the backend directory
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
