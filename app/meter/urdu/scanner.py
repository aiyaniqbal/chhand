"""Public API for Urdu Arooz prosody, Bahr matching, and Taqti analysis."""

from app.meter.urdu.bahr import BAHRS, get_bahr, list_bahrs
from app.meter.urdu.qafiya import extract_qafiya, extract_radif
from app.meter.urdu.taqti import UrduScansionResult, scan_urdu_line


def suggest_bahrs(text: str) -> list[dict]:
    """Suggest likely matching Bahrs for an Urdu line with similarity scores."""
    result = scan_urdu_line(text)
    suggestions: list[dict] = []
    if result.matched_bahr and result.matched_bahr_name:
        suggestions.append(
            {
                "id": result.matched_bahr,
                "name": result.matched_bahr_name,
                "similarity": 1.0,
            }
        )
    suggestions.extend(result.alternative_bahrs)
    return suggestions


def analyze_ghazal(couplets: list[tuple[str, str]]) -> dict:
    """Analyze a multi-couplet Ghazal for meter consistency, Radif, and Qafiya."""
    misras: list[str] = []
    for m1, m2 in couplets:
        if m1.strip():
            misras.append(m1.strip())
        if m2.strip():
            misras.append(m2.strip())

    scans = [scan_urdu_line(m) for m in misras]
    qafiya_info = extract_qafiya(misras)

    # Check meter uniformity across couplets
    detected_bahrs = [s.matched_bahr for s in scans if s.matched_bahr]
    dominant_bahr = max(set(detected_bahrs), key=detected_bahrs.count) if detected_bahrs else None

    return {
        "misras_count": len(misras),
        "dominant_bahr": dominant_bahr,
        "scans": [
            {
                "text": s.original_text,
                "bahr": s.matched_bahr,
                "confidence": s.confidence,
                "pattern": s.weight_pattern,
            }
            for s in scans
        ],
        "qafiya": qafiya_info,
    }


__all__ = [
    "BAHRS",
    "UrduScansionResult",
    "analyze_ghazal",
    "extract_qafiya",
    "extract_radif",
    "get_bahr",
    "list_bahrs",
    "scan_urdu_line",
    "suggest_bahrs",
]
