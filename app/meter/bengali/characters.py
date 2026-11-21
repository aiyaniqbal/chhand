"""Bengali Unicode character classifications and constants."""

INDEPENDENT_VOWELS = {"অ", "আ", "ই", "ঈ", "উ", "ঊ", "ঋ", "এ", "ঐ", "ও", "ঔ"}

VOWEL_SIGNS = {
    "\u09be": "aa",  # া
    "\u09bf": "i",  # ি
    "\u09c0": "ii",  # ী
    "\u09c1": "u",  # ু
    "\u09c2": "uu",  # ূ
    "\u09c3": "ri",  # ৃ
    "\u09c7": "e",  # ে
    "\u09c8": "ai",  # ৈ
    "\u09cb": "o",  # ো
    "\u09cc": "au",  # ৌ
}

CONSONANTS = {
    "ক",
    "খ",
    "গ",
    "ঘ",
    "ঙ",
    "চ",
    "ছ",
    "জ",
    "ঝ",
    "ঞ",
    "ট",
    "ঠ",
    "ড",
    "ঢ",
    "ণ",
    "ত",
    "থ",
    "দ",
    "ধ",
    "ন",
    "প",
    "ফ",
    "ব",
    "ভ",
    "ম",
    "য",
    "র",
    "ল",
    "শ",
    "ষ",
    "স",
    "হ",
    "ড়",
    "ঢ়",
    "য়",
    "ৎ",
}

HASANTA = "\u09cd"  # ্ Virama / Hasanta
ANUSVARA = "\u0982"  # ং
VISARGA = "\u0983"  # ঃ
CHANDRABINDU = "\u0981"  # ঁ
NUKTA = "\u09bc"

MODIFIERS = {ANUSVARA, VISARGA, CHANDRABINDU, NUKTA}


def is_independent_vowel(ch: str) -> bool:
    """Return True if character is an independent Bengali vowel."""
    return ch in INDEPENDENT_VOWELS


def is_vowel_sign(ch: str) -> bool:
    """Return True if character is a dependent Bengali vowel sign (Matra)."""
    return ch in VOWEL_SIGNS


def is_consonant(ch: str) -> bool:
    """Return True if character is a Bengali consonant."""
    return ch in CONSONANTS


def is_hasanta(ch: str) -> bool:
    """Return True if character is Hasanta (Virama)."""
    return ch == HASANTA


def classify_char(ch: str) -> str:
    """Return classification label for a character."""
    if is_independent_vowel(ch):
        return "vowel"
    if is_vowel_sign(ch):
        return "vowel_sign"
    if is_consonant(ch):
        return "consonant"
    if is_hasanta(ch):
        return "hasanta"
    if ch in MODIFIERS:
        return "modifier"
    if ch in {" ", "\t", "\n", ",", ";", ".", "!", "?", "।", "॥", "-"}:
        return "punctuation"
    return "other"
