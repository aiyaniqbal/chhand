"""Supported languages and metadata for Gemini Text-to-Speech recitation."""

SUPPORTED_LANGUAGES: dict[str, dict[str, str]] = {
    "hi": {
        "lang_code": "hi-IN",
        "name": "Hindi",
        "status": "supported",
    },
    "bn": {
        "lang_code": "bn-IN",
        "name": "Bengali",
        "status": "supported",
    },
    "ur": {
        "lang_code": "ur-PK",
        "name": "Urdu",
        "status": "experimental",
    },
}


def is_tts_supported(language: str) -> bool:
    """Return True if TTS is available (supported or experimental) for the language."""
    return language in SUPPORTED_LANGUAGES


def get_tts_lang_code(language: str) -> str | None:
    """Return BCP-47 language code for TTS model, or None if unsupported."""
    info = SUPPORTED_LANGUAGES.get(language)
    return info["lang_code"] if info else None


def get_tts_status(language: str) -> str:
    """Return status: 'supported', 'experimental', or 'unsupported'."""
    info = SUPPORTED_LANGUAGES.get(language)
    return info["status"] if info else "unsupported"
