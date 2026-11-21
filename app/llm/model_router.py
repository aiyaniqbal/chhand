"""Route language-specific generation requests to the best available Gemini model."""

from app.config import settings

# Map language codes to their optional fine-tuned model setting attribute
_LANG_MODEL_ATTRS: dict[str, str] = {
    "hi": "GEMINI_TUNED_HINDI_MODEL",
    "ur": "GEMINI_TUNED_URDU_MODEL",
    "bn": "GEMINI_TUNED_BENGALI_MODEL",
}


def get_model_for_language(language: str) -> str:
    """
    Return the best Gemini model name for the given BCP-47 language code.

    Resolution order:
    1. If ENABLE_FINE_TUNED_MODEL is True and a language-specific tuned model is
       configured (e.g. GEMINI_TUNED_HINDI_MODEL), return that model.
    2. Fall back to the global GEMINI_MODEL setting.
    """
    if settings.ENABLE_FINE_TUNED_MODEL:
        attr = _LANG_MODEL_ATTRS.get(language, "")
        if attr:
            tuned_model: str = getattr(settings, attr, "").strip()
            if tuned_model:
                return tuned_model

    return settings.GEMINI_MODEL
