"""Urdu text normalization preserving lexical and prosodic identity."""

import unicodedata

# Mapping from Arabic forms to canonical Urdu forms
_CHAR_MAP = {
    "\u064a": "ی",  # Arabic Yeh -> Urdu Chhoti Ye
    "\u0649": "ی",  # Alef Maksura -> Urdu Chhoti Ye
    "\u0643": "ک",  # Arabic Kaf -> Urdu Keheh
    "\u0629": "ہ",  # Teh Marbuta -> Urdu Heh
    "\u0623": "ا",  # Alef with Hamza Above -> Alef
    "\u0625": "ا",  # Alef with Hamza Below -> Alef
    "\u0622": "آ",  # Alef with Madda -> Canonical Alif Madda
    "\u06c1": "ہ",  # Heh Goal
    "\u06be": "ھ",  # Do Chashmi Heh
}


def normalize_urdu(text: str) -> str:
    """
    Normalize Urdu text to NFC and replace non-standard Arabic glyph variants with
    canonical Urdu characters while preserving diacritics and source positions.
    """
    if not text:
        return ""

    # Normalize Unicode composition to NFC
    nfc = unicodedata.normalize("NFC", text)

    # Normalize character variants
    chars: list[str] = []
    for ch in nfc:
        chars.append(_CHAR_MAP.get(ch, ch))

    return "".join(chars)
