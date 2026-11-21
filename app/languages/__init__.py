"""Languages package — multilingual capability registry."""

from app.languages.capabilities import filter_by_feature, get_tts_lang_code, supports_poem_form
from app.languages.models import LanguageCapability
from app.languages.registry import LANGUAGES, get_all_languages, get_language, is_supported

__all__ = [
    "LANGUAGES",
    "LanguageCapability",
    "get_language",
    "get_all_languages",
    "is_supported",
    "filter_by_feature",
    "supports_poem_form",
    "get_tts_lang_code",
]
