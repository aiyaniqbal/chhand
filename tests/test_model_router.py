"""Tests for model routing between base Gemini and language-tuned models."""

from app.config import settings
from app.llm.model_router import get_model_for_language


def test_model_router_default_fallback(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_FINE_TUNED_MODEL", False)
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-3.8-flash")

    assert get_model_for_language("hi") == "gemini-3.8-flash"
    assert get_model_for_language("ur") == "gemini-3.8-flash"
    assert get_model_for_language("bn") == "gemini-3.8-flash"


def test_model_router_tuned_override(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_FINE_TUNED_MODEL", True)
    monkeypatch.setattr(
        settings,
        "GEMINI_TUNED_HINDI_MODEL",
        "projects/123/locations/us-central1/models/tuned-hi-v1",
    )
    monkeypatch.setattr(settings, "GEMINI_TUNED_URDU_MODEL", "")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-3.8-flash")

    # Hindi should route to tuned model
    assert get_model_for_language("hi") == "projects/123/locations/us-central1/models/tuned-hi-v1"
    # Urdu has no tuned model, should fall back to base
    assert get_model_for_language("ur") == "gemini-3.8-flash"
