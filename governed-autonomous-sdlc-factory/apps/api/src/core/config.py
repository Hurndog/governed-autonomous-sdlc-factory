"""Application configuration using pydantic-settings."""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="postgresql+asyncpg://governance:forge@localhost:5432/sdlc_factory")
    redis_url: str = Field(default="redis://localhost:6379/0")

    # JWT
    jwt_secret: str = Field(default="change-me-in-production-minimum-32-bytes-long!!")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiry_minutes: int = Field(default=60)

    # GitHub
    github_token: Optional[str] = Field(default=None)
    github_owner: Optional[str] = Field(default=None)
    github_repo: Optional[str] = Field(default=None)

    # OMI
    omi_api_url: Optional[str] = Field(default=None)
    omi_api_key: Optional[str] = Field(default=None)

    # LLM Providers
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    ollama_base_url: str = Field(default="http://localhost:11434")

    # ── Safety Guard Configuration ──
    # Bounded-runtime limits — NOT arbitrary iteration caps.
    # The runtime stops because of timeout/budget/convergence, NOT "iteration 60."

    # Timeout-based guards
    pipeline_timeout_seconds: int = Field(default=3600)  # 1 hour max per pipeline
    phase_timeout_seconds: int = Field(default=600)      # 10 min max per phase
    replay_timeout_seconds: int = Field(default=300)     # 5 min max per replay

    # Budget-based guards
    max_tokens_per_run: int = Field(default=5_000_000)   # 5M tokens max per run
    max_model_calls_per_phase: int = Field(default=100)  # 100 model calls per phase
    max_total_model_calls_per_run: int = Field(default=500)  # 500 total model calls per run
    max_artifacts_per_run: int = Field(default=200)      # 200 artifacts max per run
    max_events_per_run: int = Field(default=1000)        # 1000 events max per run

    # Retry-based guards
    max_retries_per_phase: int = Field(default=3)        # 3 retries per phase

    # Convergence-based guards (semantic/mutation)
    # These are NOT iteration caps — they are stall detection limits.
    # The runtime should converge long before hitting these.
    max_semantic_iterations: int = Field(default=50)     # Semantic refinement stall detection
    max_mutation_iterations: int = Field(default=30)     # Mutation testing stall detection

    # Convergence detection
    semantic_convergence_threshold: float = Field(default=0.95)  # Stop when coverage stabilizes
    semantic_convergence_window: int = Field(default=5)          # Check last N iterations for convergence
    mutation_convergence_threshold: float = Field(default=0.90)  # Stop when mutation score stabilizes

    # Progress detection (stall detection)
    progress_check_interval: int = Field(default=10)     # Check progress every N iterations
    max_stall_iterations: int = Field(default=20)         # Stop if no progress for N iterations

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
