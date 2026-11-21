"""Language capability registry for Chhand multilingual poetry studio."""

from app.languages.models import LanguageCapability

LANGUAGES: dict[str, dict] = {
    "hi": {
        "name": "Hindi",
        "native_name": "हिन्दी",
        "script": "Devanagari",
        "direction": "ltr",
        "meter_systems": ["matra"],
        "poem_forms": ["doha", "chaupai", "custom", "free_verse"],
        "scanner_available": True,
        "rhyme_available": True,
        "tts_status": "supported",
        "tts_lang_code": "hi-IN",
        "export_available": True,
        "generator_available": True,
    },
    "ur": {
        "name": "Urdu",
        "native_name": "اردو",
        "script": "Nastaliq",
        "direction": "rtl",
        "meter_systems": ["arooz"],
        "poem_forms": ["ghazal", "nazm", "free_verse"],
        "scanner_available": True,
        "rhyme_available": True,
        "tts_status": "experimental",
        "tts_lang_code": "ur-PK",
        "export_available": True,
        "generator_available": True,
    },
    "bn": {
        "name": "Bengali",
        "native_name": "বাংলা",
        "script": "Bengali",
        "direction": "ltr",
        "meter_systems": ["aksharbritta", "matrabritta", "swarobritta"],
        "poem_forms": ["aksharbritta", "matrabritta", "swarobritta", "free_verse"],
        "scanner_available": True,
        "rhyme_available": False,
        "tts_status": "supported",
        "tts_lang_code": "bn-IN",
        "export_available": True,
        "generator_available": True,
    },
}


def get_language(code: str) -> LanguageCapability | None:
    """Return LanguageCapability for a BCP-47 language code, or None if unsupported."""
    data = LANGUAGES.get(code)
    if data is None:
        return None
    return LanguageCapability(language_code=code, **data)


def get_all_languages() -> list[LanguageCapability]:
    """Return all registered language capabilities."""
    return [LanguageCapability(language_code=code, **data) for code, data in LANGUAGES.items()]


def is_supported(code: str) -> bool:
    """Return True if the given language code is registered."""
    return code in LANGUAGES
