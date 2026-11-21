"""Urdu prosodic weight pattern calculation and confidence metrics."""

from app.meter.urdu.diacritics import has_diacritics
from app.meter.urdu.lexicon import lookup_word_pattern
from app.meter.urdu.syllables import syllabify_urdu


def line_to_weight_pattern(text: str) -> str:
    """
    Convert an Urdu line into a string pattern of Short (S) and Long (L) weights.
    Example: 'SLSLLSLS'.
    """
    syllables = syllabify_urdu(text)
    pattern_chars: list[str] = []
    for s in syllables:
        if s.weight == "short":
            pattern_chars.append("S")
        elif s.weight == "long":
            pattern_chars.append("L")
        elif s.weight == "overlong":
            pattern_chars.extend(["L", "S"])
        else:
            pattern_chars.append("L")  # Default ambiguity to long
    return "".join(pattern_chars)


def pattern_confidence(text: str) -> float:
    """
    Calculate confidence score (0.0 to 1.0) for the scansion of an Urdu line.
    Higher when Harakat are present or words exist in the reviewed lexicon.
    """
    words = [w for w in text.split() if w.strip()]
    if not words:
        return 0.0

    lexicon_matches = sum(1 for w in words if lookup_word_pattern(w) is not None)
    ratio = lexicon_matches / len(words)

    confidence = 0.5 + 0.3 * ratio
    if has_diacritics(text):
        confidence = min(1.0, confidence + 0.2)

    return round(confidence, 2)
