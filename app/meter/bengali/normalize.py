"""Bengali Unicode normalization and script cleanup."""

import unicodedata


def normalize_bengali(text: str) -> str:
    """
    Normalize Bengali text into canonical Unicode NFC form.
    Handles legacy composited or decomposing sequences.
    """
    if not text:
        return ""
    # NFC canonical normalization
    return unicodedata.normalize("NFC", text)
