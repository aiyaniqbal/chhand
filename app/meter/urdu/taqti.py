"""Urdu Taqti (scansion) engine matching poetic lines against Bahr templates."""

from dataclasses import dataclass
from typing import Any

from app.meter.urdu.bahr import BAHRS, get_bahr
from app.meter.urdu.normalize import normalize_urdu
from app.meter.urdu.prosody import line_to_weight_pattern, pattern_confidence
from app.meter.urdu.syllables import syllabify_urdu


@dataclass
class UrduScansionResult:
    """Detailed scansion result for an Urdu poetic hemistich (Misra)."""

    original_text: str
    normalized_text: str
    words: list[str]
    syllables: list[dict[str, Any]]
    weight_pattern: str
    matched_bahr: str | None
    matched_bahr_name: str | None
    alternative_bahrs: list[dict[str, Any]]
    arkan_mapping: list[str]
    explanation: str
    confidence: float
    ambiguity_note: str
    source_positions: list[tuple[int, int]]


def _pattern_similarity(p1: str, p2: str) -> float:
    """Calculate normalized similarity between two weight patterns."""
    if not p1 or not p2:
        return 0.0
    common_len = min(len(p1), len(p2))
    matches = sum(1 for i in range(common_len) if p1[i] == p2[i])
    max_len = max(len(p1), len(p2))
    return matches / max_len


def scan_urdu_line(text: str, bahr: str | None = None) -> UrduScansionResult:
    """
    Perform Taqti (scansion) on a single Urdu line (Misra).
    If bahr is specified, checks against that specific Bahr; otherwise identifies the best matching Bahr.
    """
    original = text
    norm = normalize_urdu(text)
    words = [w for w in norm.split() if w.strip()]

    sylls = syllabify_urdu(norm)
    syll_dicts = [
        {
            "text": s.text,
            "weight": s.weight,
            "source_start": s.source_start,
            "source_end": s.source_end,
        }
        for s in sylls
    ]
    source_positions = [(s.source_start, s.source_end) for s in sylls]

    weight_pat = line_to_weight_pattern(norm)
    conf = pattern_confidence(norm)

    ambiguity_note = ""
    if conf < 0.7:
        ambiguity_note = (
            "Urdu poetry frequently omits short-vowel marks (Harakat). "
            "Pronunciation weights are estimated from orthography and the standard lexicon."
        )

    # Evaluate against Bahrs
    ranked_bahrs: list[tuple[str, float, str]] = []
    for b_id, b_def in BAHRS.items():
        sim = _pattern_similarity(weight_pat, b_def.pattern)
        ranked_bahrs.append((b_id, sim, b_def.name))

    ranked_bahrs.sort(key=lambda x: x[1], reverse=True)

    matched_bahr_id: str | None = None
    matched_bahr_name: str | None = None
    arkan_map: list[str] = []
    explanation = ""

    if bahr:
        target_bahr = get_bahr(bahr)
        if target_bahr:
            sim = _pattern_similarity(weight_pat, target_bahr.pattern)
            matched_bahr_id = target_bahr.id
            matched_bahr_name = target_bahr.name
            arkan_map = target_bahr.arkan
            if sim >= 0.85:
                explanation = f"Misra matches {target_bahr.name} ({target_bahr.urdu_name}) with {int(sim * 100)}% adherence."
            else:
                explanation = (
                    f"Misra pattern '{weight_pat}' differs from expected '{target_bahr.pattern}' "
                    f"for {target_bahr.name}."
                )
        else:
            explanation = f"Unknown Bahr '{bahr}'. Evaluated against standard catalog."
    elif ranked_bahrs and ranked_bahrs[0][1] >= 0.75:
        best_id, best_sim, best_name = ranked_bahrs[0]
        matched_bahr_id = best_id
        matched_bahr_name = best_name
        b_def = BAHRS[best_id]
        arkan_map = b_def.arkan
        explanation = f"Best matching meter is {best_name} ({b_def.urdu_name}) with {int(best_sim * 100)}% adherence."
    else:
        explanation = (
            f"Pattern '{weight_pat}' did not conclusively match a standard reviewed Bahr. "
            "Consider adding diacritics (Zabar/Zer/Pesh) to disambiguate vowel weights."
        )

    alternatives = [
        {"id": b_id, "name": name, "similarity": round(sim, 2)}
        for b_id, sim, name in ranked_bahrs[:3]
        if b_id != matched_bahr_id
    ]

    return UrduScansionResult(
        original_text=original,
        normalized_text=norm,
        words=words,
        syllables=syll_dicts,
        weight_pattern=weight_pat,
        matched_bahr=matched_bahr_id,
        matched_bahr_name=matched_bahr_name,
        alternative_bahrs=alternatives,
        arkan_mapping=arkan_map,
        explanation=explanation,
        confidence=conf,
        ambiguity_note=ambiguity_note,
        source_positions=source_positions,
    )
