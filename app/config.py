from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ScrapLedger"
    environment: str = "local"  # local | ci | production
    database_url: str = "postgresql://postgres:postgres@localhost:5432/scrapledger"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    primary_model: str = "gemini/gemini-flash-latest"
    llm_timeout: float = 10.0
    llm_retries: int = 3


@lru_cache
def get_settings() -> Settings:
    return Settings()
