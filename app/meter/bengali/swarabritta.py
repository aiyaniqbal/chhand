"""Swarabritta (স্বরবৃত্ত / দলবৃত্ত) meter analysis for Bengali rhythmic poetry."""

from app.meter.bengali.syllables import syllabify_bengali_dals


def swarabritta_count(text: str) -> int:
    """
    Count the number of rhythmic pulse units (Dal / দল) in Swarabritta.
    In Swarabritta, both open and closed syllables generally carry equal single-beat pulse weight.
    """
    dals = syllabify_bengali_dals(text)
    return len(dals)


def scan_swarabritta(text: str, target_pulses: int = 8) -> dict:
    """
    Scan a line against a target pulse count under Swarabritta rules (e.g. 4+4=8 or 4+4+4+2=14).
    """
    dals = syllabify_bengali_dals(text)
    count = len(dals)
    diff = count - target_pulses

    if diff == 0:
        status = "matched"
        diagnostic = f"Matches target {target_pulses} pulses (dal)."
    elif diff > 0:
        status = "over"
        diagnostic = f"Line has {count} pulses ({diff} over target {target_pulses})."
    else:
        status = "under"
        diagnostic = f"Line has {count} pulses ({abs(diff)} under target {target_pulses})."

    return {
        "count": count,
        "target": target_pulses,
        "diff": diff,
        "status": status,
        "diagnostic": diagnostic,
    }
