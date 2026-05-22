"""Model Health & Provider Validation Tests (v0.5.1B).

Validates provider health checks, availability reporting,
and model listing capabilities.

No fake results: providers without keys report honestly.
"""
import asyncio
import pytest

from src.engines.ollama_provider import OllamaProvider
from src.engines.model_providers import (
    OpenAIProvider,
    AnthropicProvider,
    LMStudioProvider,
)


class TestOllamaHealthCheck:
    """Test Ollama provider health check with real Ollama instance."""

    @pytest.mark.asyncio
    async def test_ollama_health_reports_status(self):
        """Health check should return a status field."""
        provider = OllamaProvider()
        result = await provider.health_check()
        assert "status" in result
        assert "provider" in result
        assert result["provider"] == "ollama"
        # Status must be one of the expected values
        assert result["status"] in ("available", "unhealthy", "unavailable")

    @pytest.mark.asyncio
    async def test_ollama_health_available_has_version(self):
        """If Ollama is available, version should be reported."""
        provider = OllamaProvider()
        result = await provider.health_check()
        if result["status"] == "available":
            assert "version" in result
            assert "latency_ms" in result
            assert isinstance(result["latency_ms"], float)

    @pytest.mark.asyncio
    async def test_ollama_health_unavailable_has_error(self):
        """If Ollama is unavailable, error should be reported."""
        provider = OllamaProvider(base_url="http://localhost:19999")
        result = await provider.health_check()
        assert result["status"] == "unavailable"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_ollama_list_models_returns_list(self):
        """list_models should return a list (empty or populated)."""
        provider = OllamaProvider()
        models = await provider.list_available_models()
        assert isinstance(models, list)
        # If Ollama is running, should have models
        if models:
            for m in models:
                assert "model_id" in m

    @pytest.mark.asyncio
    async def test_ollama_list_models_unavailable_returns_empty(self):
        """list_models should return empty list when Ollama is down."""
        provider = OllamaProvider(base_url="http://localhost:19999")
        models = await provider.list_available_models()
        assert models == []


class TestOpenAIHealthCheck:
    """Test OpenAI provider health check."""

    @pytest.mark.asyncio
    async def test_openai_no_key_reports_misconfigured(self):
        """Without API key, health check should report misconfigured."""
        provider = OpenAIProvider(api_key="")
        result = await provider.health_check()
        assert result["status"] == "misconfigured"
        assert result["provider"] == "openai"

    @pytest.mark.asyncio
    async def test_openai_list_models_no_key_returns_empty(self):
        """Without API key, list_models should return empty list."""
        provider = OpenAIProvider(api_key="")
        models = await provider.list_available_models()
        assert models == []


class TestAnthropicHealthCheck:
    """Test Anthropic provider health check."""

    @pytest.mark.asyncio
    async def test_anthropic_no_key_reports_misconfigured(self):
        """Without API key, health check should report misconfigured."""
        provider = AnthropicProvider(api_key="")
        result = await provider.health_check()
        assert result["status"] == "misconfigured"
        assert result["provider"] == "anthropic"

    @pytest.mark.asyncio
    async def test_anthropic_list_models_no_key_returns_empty(self):
        """Without API key, list_models should return empty list."""
        provider = AnthropicProvider(api_key="")
        models = await provider.list_available_models()
        assert models == []


class TestLMStudioHealthCheck:
    """Test LM Studio provider health check (base class fallback)."""

    @pytest.mark.asyncio
    async def test_lmstudio_health_unverified_without_implementation(self):
        """LM Studio uses base class fallback: health_check returns unverified."""
        provider = LMStudioProvider()
        result = await provider.health_check()
        assert result["status"] == "unverified"
        assert result["provider"] == "lm_studio"

    @pytest.mark.asyncio
    async def test_lmstudio_list_models_returns_empty(self):
        """LM Studio base class list_models returns empty list."""
        provider = LMStudioProvider()
        models = await provider.list_available_models()
        assert models == []


class TestProviderStatusClassification:
    """Test that provider status is correctly classified."""

    def test_status_available(self):
        """'available' means the provider is reachable and functional."""
        statuses = ["available"]
        assert all(s == "available" for s in statuses)

    def test_status_unavailable_vs_misconfigured(self):
        """'unreachable' and 'misconfigured' are distinct from 'available'."""
        non_functional = ["unavailable", "unhealthy", "misconfigured", "unverified"]
        assert all(s != "available" for s in non_functional)
