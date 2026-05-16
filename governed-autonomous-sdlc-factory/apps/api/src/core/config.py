"""Application configuration using pydantic-settings."""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="postgresql+asyncpg://governance:forge@localhost:5432/sdlc_factory")
    redis_url: str = Field(default="redis://localhost:6379/0")
    qdrant_url: str = Field(default="http://localhost:6333")

    # Model Provider API Keys
    lm_studio_url: str = Field(default="http://localhost:1234/v1")
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    openrouter_api_key: str = Field(default="")

    # Model Routing Defaults
    default_model_provider: str = Field(default="lm_studio")
    default_model_id: str = Field(default="local-model")
    max_tokens_default: int = Field(default=4096)
    temperature_default: float = Field(default=0.7)

    # API
    api_cors_origins: str = Field(default="http://localhost:3000")
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    # GitHub
    github_token: str = Field(default="")
    github_owner: str = Field(default="")
    github_repo: str = Field(default="")

    # OMI
    omi_api_url: str = Field(default="")
    omi_api_key: str = Field(default="")

    # LangGraph
    langgraph_checkpoint_url: str = Field(default="")

    @property
    def github_configured(self) -> bool:
        return bool(self.github_token and self.github_owner)

    @property
    def omi_configured(self) -> bool:
        return bool(self.omi_api_url and self.omi_api_key)

    @property
    def openai_configured(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def anthropic_configured(self) -> bool:
        return bool(self.anthropic_api_key)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}


settings = Settings()
