"""Public Bengali Chhanda scanner unifying Aksharbritta, Matrabritta, and Swarabritta."""

from dataclasses import dataclass
from typing import Any

from app.meter.bengali.aksharbritta import scan_aksharbritta
from app.meter.bengali.matrabritta import scan_matrabritta
from app.meter.bengali.normalize import normalize_bengali
from app.meter.bengali.swarabritta import scan_swarabritta
from app.meter.bengali.syllables import syllabify_bengali
from app.meter.bengali.templates import BENGALI_TEMPLATES, get_bengali_template


@dataclass
class BengaliScansionResult:
    """Comprehensive scansion result for a single line of Bengali poetry."""

    original_text: str
    normalized_text: str
    aksharas: list[str]
    syllable_grouping: list[dict[str, Any]]
    count_value: int
    count_unit: str  # "aksharas", "matras", "dals"
    template_name: str
    target_count: int
    difference: int
    status: str  # "matched", "over", "under", "unvalidated"
    break_positions: list[int]
    diagnostic_message: str
    ambiguity_status: str
    source_spans: list[tuple[int, int]]
    system: str  # "aksharbritta", "matrabritta", "swarobritta"


def scan_bengali_line(
    text: str,
    meter_template: str | None = None,
) -> BengaliScansionResult:
    """
    Scan a line of Bengali poetry against a specified or default Chhanda template.
    Defaults to 'payar' (14-akshara Aksharbritta) if no template is specified.
    """
    original = text
    norm = normalize_bengali(text)

    tmpl_id = meter_template or "payar"
    tmpl = get_bengali_template(tmpl_id) or BENGALI_TEMPLATES["payar"]

    sylls = syllabify_bengali(norm)
    akshara_texts = [s.text for s in sylls]
    source_spans = [(s.source_start, s.source_end) for s in sylls]
    syll_dicts = [
        {
            "text": s.text,
            "is_open": s.is_open,
            "is_conjunct": s.is_conjunct,
            "source_start": s.source_start,
            "source_end": s.source_end,
        }
        for s in sylls
    ]

    break_positions: list[int] = []

    if tmpl.system == "aksharbritta":
        scan = scan_aksharbritta(norm, tmpl.target_count)
        count_val = scan["count"]
        diff = scan["diff"]
        status = scan["status"]
        diag = scan["diagnostic"]
        break_positions = scan.get("break_positions", [])
    elif tmpl.system == "matrabritta":
        scan = scan_matrabritta(norm, tmpl.target_count)
        count_val = scan["count"]
        diff = scan["diff"]
        status = scan["status"]
        diag = scan["diagnostic"]
    elif tmpl.system == "swarobritta":
        scan = scan_swarabritta(norm, tmpl.target_count)
        count_val = scan["count"]
        diff = scan["diff"]
        status = scan["status"]
        diag = scan["diagnostic"]
    else:
        count_val = len(sylls)
        diff = count_val - tmpl.target_count
        status = "matched" if diff == 0 else ("over" if diff > 0 else "under")
        diag = f"Measured {count_val} {tmpl.unit_name} against target {tmpl.target_count}."

    ambiguity_status = "clear"
    if any(s.is_conjunct for s in sylls) and tmpl.system == "matrabritta":
        ambiguity_status = "contains_conjuncts"

    return BengaliScansionResult(
        original_text=original,
        normalized_text=norm,
        aksharas=akshara_texts,
        syllable_grouping=syll_dicts,
        count_value=count_val,
        count_unit=tmpl.unit_name,
        template_name=tmpl.name,
        target_count=tmpl.target_count,
        difference=diff,
        status=status,
        break_positions=break_positions,
        diagnostic_message=diag,
        ambiguity_status=ambiguity_status,
        source_spans=source_spans,
        system=tmpl.system,
    )
