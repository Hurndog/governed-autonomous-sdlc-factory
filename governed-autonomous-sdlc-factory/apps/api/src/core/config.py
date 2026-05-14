"""Application configuration using pydantic-settings."""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="postgresql+asyncpg://governance:forge@localhost:5432/sdlc_factory")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Qdrant
    qdrant_url: str = Field(default="http://localhost:6333")
    qdrant_collection: str = Field(default="sdlc_memory")

    # GitHub
    github_token: Optional[str] = Field(default=None)
    github_owner: Optional[str] = Field(default=None)
    github_repo: Optional[str] = Field(default=None)

    # Local AI - LM Studio
    lm_studio_base_url: str = Field(default="http://localhost:1234/v1")
    lm_studio_model: str = Field(default="local-model")

    # Claude
    claude_api_key: Optional[str] = Field(default=None)

    # Model Provider
    default_model_provider: str = Field(default="local")
    local_only_mode: bool = Field(default=True)

    # Cost Controls
    cost_hard_limit: float = Field(default=50.0)
    cost_warning_threshold: float = Field(default=0.8)

    # Memory Integrations
    obsidian_vault_path: Optional[str] = Field(default=None)
    omi_api_url: Optional[str] = Field(default=None)
    omi_api_key: Optional[str] = Field(default=None)

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_secret_key: str = Field(default="change-me-in-production")
    api_cors_origins: str = Field(default="http://localhost:3000")

    # Observability
    otel_exporter_otlp_endpoint: Optional[str] = Field(default="http://localhost:4317")
    prometheus_port: int = Field(default=9090)
    grafana_port: int = Field(default=3001)
    loki_port: int = Field(default=3100)

    # Deployment
    deployment_base_port: int = Field(default=9000)
    docker_network: str = Field(default="sdlc-factory")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    @property
    def github_configured(self) -> bool:
        return bool(self.github_token and self.github_owner)

    @property
    def omi_configured(self) -> bool:
        return bool(self.omi_api_url and self.omi_api_key)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
