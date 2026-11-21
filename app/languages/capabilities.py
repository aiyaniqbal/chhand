"""Helper functions for querying language capabilities."""

from app.languages.models import LanguageCapability


def filter_by_feature(
    languages: list[LanguageCapability],
    *,
    generator: bool | None = None,
    scanner: bool | None = None,
    rhyme: bool | None = None,
    tts: bool | None = None,
) -> list[LanguageCapability]:
    """Filter a list of LanguageCapability objects by enabled features."""
    result = languages
    if generator is not None:
        result = [lang for lang in result if lang.generator_available == generator]
    if scanner is not None:
        result = [lang for lang in result if lang.scanner_available == scanner]
    if rhyme is not None:
        result = [lang for lang in result if lang.rhyme_available == rhyme]
    if tts is not None:
        tts_statuses = {"supported", "experimental"} if tts else {"unsupported"}
        result = [lang for lang in result if lang.tts_status in tts_statuses]
    return result


def supports_poem_form(language_code: str, form: str) -> bool:
    """Return True if the given language supports a particular poem form."""
    from app.languages.registry import LANGUAGES  # local import to avoid circular refs

    lang = LANGUAGES.get(language_code, {})
    return form in lang.get("poem_forms", [])


def get_tts_lang_code(language_code: str) -> str | None:
    """Return the BCP-47 TTS language code for the given language, or None."""
    from app.languages.registry import LANGUAGES

    lang = LANGUAGES.get(language_code, {})
    code = lang.get("tts_lang_code", "")
    return code if code else None
