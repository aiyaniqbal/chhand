"""Application runtime configuration and Gemini environment settings."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root if present
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


class Settings:
    """Application runtime configuration."""

    PROJECT_NAME: str = "Chhand"
    VERSION: str = "1.0.0"
    ENV: str = os.getenv("ENV", "development")

    # Primary Google Gemini Configuration
    # Supports GEMINI_API_KEY with legacy LLM_API_KEY fallback
    GEMINI_API_KEY: str = (
        os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("LLM_API_KEY", "").strip()
    )
    # Default to gemini-3.8-flash with legacy fallback
    GEMINI_MODEL: str = (
        os.getenv("GEMINI_MODEL", "").strip()
        or os.getenv("LLM_MODEL", "").strip()
        or "gemini-3.8-flash"
    )
    GEMINI_TIMEOUT_SECONDS: float = float(
        os.getenv("GEMINI_TIMEOUT_SECONDS", "") or os.getenv("LLM_TIMEOUT_SECONDS", "30.0")
    )
    GEMINI_MAX_CANDIDATES: int = int(os.getenv("GEMINI_MAX_CANDIDATES", "4"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    # TTS model configuration
    GEMINI_TTS_MODEL: str = os.getenv("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
    GEMINI_TTS_LITE_MODEL: str = os.getenv("GEMINI_TTS_LITE_MODEL", "gemini-3.8-flash-lite-tts")
    GEMINI_TTS_TIMEOUT_SECONDS: float = float(os.getenv("GEMINI_TTS_TIMEOUT_SECONDS", "60.0"))

    # Fine-tuned / tuned model overrides per language
    GEMINI_TUNED_HINDI_MODEL: str = os.getenv("GEMINI_TUNED_HINDI_MODEL", "")
    GEMINI_TUNED_URDU_MODEL: str = os.getenv("GEMINI_TUNED_URDU_MODEL", "")
    GEMINI_TUNED_BENGALI_MODEL: str = os.getenv("GEMINI_TUNED_BENGALI_MODEL", "")

    # Google Cloud (Vertex AI) configuration
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    # Feature flags
    ENABLE_POETRY_GENERATION: bool = os.getenv("ENABLE_POETRY_GENERATION", "true").lower() == "true"
    ENABLE_TTS: bool = os.getenv("ENABLE_TTS", "true").lower() == "true"
    ENABLE_URDU: bool = os.getenv("ENABLE_URDU", "true").lower() == "true"
    ENABLE_BENGALI: bool = os.getenv("ENABLE_BENGALI", "true").lower() == "true"
    ENABLE_FINE_TUNED_MODEL: bool = os.getenv("ENABLE_FINE_TUNED_MODEL", "false").lower() == "true"

    # Legacy attributes for backward compatibility
    @property
    def LLM_API_KEY(self) -> str:
        return self.GEMINI_API_KEY

    @property
    def LLM_MODEL(self) -> str:
        return self.GEMINI_MODEL

    @property
    def LLM_TIMEOUT_SECONDS(self) -> float:
        return self.GEMINI_TIMEOUT_SECONDS

    # Meter defaults
    DEFAULT_PRONUNCIATION_MODE: str = "orthographic"

    @property
    def is_gemini_configured(self) -> bool:
        """Returns True if a Gemini API key is configured."""
        return bool(self.GEMINI_API_KEY)

    @property
    def is_llm_configured(self) -> bool:
        """Backward-compatible alias for is_gemini_configured."""
        return self.is_gemini_configured


settings = Settings()
