"""Pytest configuration and test fixtures for Chhand."""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.meter.templates import CHAUPAI_TEMPLATE, DOHA_TEMPLATE


@pytest.fixture
def test_client() -> TestClient:
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def doha_template():
    return DOHA_TEMPLATE


@pytest.fixture
def chaupai_template():
    return CHAUPAI_TEMPLATE


@pytest.fixture
def sample_dohas() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parent.parent / "data" / "sample_dohas.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


@pytest.fixture
def sample_chaupais() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parent.parent / "data" / "sample_chaupais.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


@pytest.fixture
def broken_examples() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parent.parent / "data" / "broken_examples.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


class MockLLMClient:
    """Mock asynchronous LLM client for tests without calling external APIs."""

    def __init__(
        self,
        response_data: dict[str, Any] | None = None,
        should_fail: bool = False,
        should_timeout: bool = False,
    ):
        self.response_data = response_data or {}
        self.should_fail = should_fail
        self.should_timeout = should_timeout
        self.is_configured = True

    async def generate_json(
        self, messages: list[dict[str, str]], temperature: float = 0.7
    ) -> dict[str, Any]:
        if self.should_timeout:
            from app.errors import LLMTimeoutError

            raise LLMTimeoutError("Mock timeout exceeded.")
        if self.should_fail:
            from app.errors import LLMProviderError

            raise LLMProviderError("Mock provider error.")
        return self.response_data


@pytest.fixture
def mock_llm_client():
    return MockLLMClient
