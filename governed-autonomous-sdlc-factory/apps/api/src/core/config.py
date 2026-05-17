"""Application configuration using pydantic-settings."""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="postgresql+asyncpg://governance:forge@localhost:5432/sdlc_factory")
    redis_url: str = Field(default="redis://localhost:6379/0")

    # GitHub
    github_token: Optional[str] = Field(default=None)
    github_owner: Optional[str] = Field(default=None)
    github_repo: Optional[str] = Field(default=None)

    # Model providers
    ollama_base_url: str = Field(default="http://localhost:11434")
    lm_studio_base_url: str = Field(default="http://localhost:1234")
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)

    # OMI
    omi_api_url: Optional[str] = Field(default=None)
    omi_api_key: Optional[str] = Field(default=None)

    # ── Operational Safety Guards ──
    # Pipeline and phase timeouts
    pipeline_timeout_seconds: int = Field(default=900)
    phase_timeout_seconds: int = Field(default=180)

    # Retry and model call limits
    max_retries_per_phase: int = Field(default=3)
    max_model_calls_per_phase: int = Field(default=5)
    max_total_model_calls_per_run: int = Field(default=50)

    # Token and budget limits
    max_tokens_per_run: int = Field(default=250000)

    # Artifact and event limits
    max_artifacts_per_run: int = Field(default=500)
    max_events_per_run: int = Field(default=10000)

    # Semantic and mutation iteration limits
    max_semantic_iterations: int = Field(default=5)
    max_mutation_iterations: int = Field(default=5)

    # Replay and background task limits
    replay_timeout_seconds: int = Field(default=300)
    background_task_lease_seconds: int = Field(default=900)
    websocket_max_reconnect_attempts: int = Field(default=10)

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
