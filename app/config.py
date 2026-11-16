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

    # LLM Configuration (OpenAI-compatible endpoints supported)
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "").strip()
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash").strip()
    LLM_BASE_URL: str = os.getenv(
        "LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
    ).strip()
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    LLM_TIMEOUT_SECONDS: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "25.0"))

    # Meter defaults
    DEFAULT_PRONUNCIATION_MODE: str = "orthographic"

    @property
    def is_llm_configured(self) -> bool:
        """Returns True if an LLM API key is provided."""
        return bool(self.LLM_API_KEY)


settings = Settings()
