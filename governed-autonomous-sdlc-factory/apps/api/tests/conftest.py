"""Pytest configuration for async test support."""
import pytest

# Register asyncio marker to avoid PytestUnknownMarkWarning
def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")
