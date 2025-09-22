from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional

SupportedProvider = Literal["openai", "groq", "anthropic", "vertex", "bedrock"]

class Settings(BaseSettings):
    # App
    APP_ENV: Literal["dev", "prod", "test"] = "dev"
    SECRET_KEY: str = "change-me-please"

    # DB / Queue
    DATABASE_URL: str
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # LLM
    LLM_PROVIDER: SupportedProvider = "openai"
    LLM_MODEL: str = "gpt-4o-mini"

    # Provider keys (optional; validated at runtime)
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    # For vertex/bedrock you’d add project/region/role config as needed

    # Browser / Policies
    HEADLESS: bool = True
    HITL_REQUIRED: bool = True
    RATE_LIMIT_GLOBAL_PER_MIN: int = 8

    # Storage (optional)
    STORAGE_PROVIDER: str = "local"
    LOCAL_STORAGE_PATH: str = "./uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
