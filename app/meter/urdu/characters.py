"""Urdu Unicode character classifications and constants for Arooz analysis."""

# Long vowels in Urdu
LONG_VOWELS = {"ا", "و", "ی", "ے", "آ"}

# Urdu / Arabic diacritics (Harakat)
HARAKAT = {
    "\u064e": "zabar",  # Fatha
    "\u0650": "zer",  # Kasra
    "\u064f": "pesh",  # Damma
    "\u0652": "sukun",  # Jazm / Sukun
    "\u0651": "tashdeed",  # Shadda
    "\u0670": "khara_zabar",  # Dagger Alif
    "\u064b": "tanween_fath",
    "\u064d": "tanween_kasr",
    "\u064c": "tanween_damm",
    "\u0654": "hamza_above",
    "\u0657": "ulta_pesh",
}

# Consonants in Urdu
CONSONANTS = {
    "ب",
    "پ",
    "ت",
    "ٹ",
    "ث",
    "ج",
    "چ",
    "ح",
    "خ",
    "د",
    "ڈ",
    "ذ",
    "ر",
    "ڑ",
    "ز",
    "ژ",
    "س",
    "ش",
    "ص",
    "ض",
    "ط",
    "ظ",
    "ع",
    "غ",
    "ف",
    "ق",
    "ک",
    "گ",
    "ل",
    "م",
    "ن",
    "ں",
    "و",
    "ہ",
    "ھ",
    "ی",
    "ے",
    "ء",
}

WORD_SEPARATORS = {" ", "\t", "\n", "،", "؛", "۔", "؟", "-", "!", ".", ":"}


def is_consonant(ch: str) -> bool:
    """Return True if the character is an Urdu consonant."""
    return ch in CONSONANTS


def is_long_vowel(ch: str) -> bool:
    """Return True if the character is a long vowel representation in Urdu."""
    return ch in LONG_VOWELS


def is_diacritic(ch: str) -> bool:
    """Return True if the character is an Arabic/Urdu short vowel or prosodic mark."""
    return ch in HARAKAT


def is_word_boundary(ch: str) -> bool:
    """Return True if the character is whitespace or punctuation."""
    return ch in WORD_SEPARATORS
