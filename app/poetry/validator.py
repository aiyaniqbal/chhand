"""Meter validation wrapper for generated poetry lines."""

import logging
from typing import Literal

from app.schemas import GeneratedLine, GenerateRequest

logger = logging.getLogger(__name__)

# Matra targets per charan for known Hindi forms
_HINDI_FORM_PATTERNS: dict[str, list[int]] = {
    "doha": [13, 11, 13, 11],
    "chaupai": [16, 16, 16, 16],
}


def _validate_hindi_line(
    text: str,
    target_matras: int,
    charan_index: int,
    pronunciation_mode: str,
) -> tuple[Literal["matched", "over", "under", "invalid"], str, int | None]:
    """
    Validate a single Hindi line using the deterministic meter scanner.
    Returns (status, note, matra_count).
    """
    try:
        from app.meter.scanner import scan_line  # local import — avoids circular deps

        result = scan_line(
            text=text,
            target_matras=target_matras,
            charan_index=charan_index,
            meter_name="custom",
            pronunciation_mode=pronunciation_mode,  # type: ignore[arg-type]
        )
        status_map = {
            "matched": "matched",
            "over": "over",
            "under": "under",
            "invalid": "invalid",
            "ambiguous": "unvalidated",
        }
        status = status_map.get(result.status, "unvalidated")
        note = "; ".join(result.diagnostics) if result.diagnostics else ""
        return status, note, result.actual_matras  # type: ignore[return-value]
    except Exception as exc:
        logger.warning("Hindi meter validation failed: %s", exc)
        return "invalid", str(exc), None


def validate_lines(
    lines: list[str],
    request: GenerateRequest,
) -> list[GeneratedLine]:
    """
    Validate a flat list of line strings against the meter/form in *request*.
    Returns a list of :class:`GeneratedLine` objects with validation metadata.
    """
    language = request.language
    form = request.poem_form
    pronunciation_mode = request.pronunciation_mode

    result: list[GeneratedLine] = []

    if language == "hi" and form in _HINDI_FORM_PATTERNS:
        pattern = _HINDI_FORM_PATTERNS[form]
        for idx, text in enumerate(lines):
            target = pattern[idx % len(pattern)]
            status, note, count = _validate_hindi_line(text, target, idx, pronunciation_mode)
            result.append(
                GeneratedLine(
                    text=text,
                    matra_count=count,
                    validation_status=status,  # type: ignore[arg-type]
                    validation_note=note,
                )
            )
    elif language == "hi" and form == "custom" and request.custom_pattern:
        pattern = request.custom_pattern
        for idx, text in enumerate(lines):
            target = pattern[idx % len(pattern)]
            status, note, count = _validate_hindi_line(text, target, idx, pronunciation_mode)
            result.append(
                GeneratedLine(
                    text=text,
                    matra_count=count,
                    validation_status=status,  # type: ignore[arg-type]
                    validation_note=note,
                )
            )
    elif language == "ur":
        from app.meter.urdu.scanner import scan_urdu_line

        for text in lines:
            try:
                urdu_scan = scan_urdu_line(text)
                if urdu_scan.matched_bahr:
                    result.append(
                        GeneratedLine(
                            text=text,
                            validation_status="matched",
                            validation_note=f"Matched {urdu_scan.matched_bahr_name}: {urdu_scan.explanation}",
                        )
                    )
                else:
                    result.append(
                        GeneratedLine(
                            text=text,
                            validation_status="unvalidated",
                            validation_note=urdu_scan.explanation,
                        )
                    )
            except Exception as exc:
                result.append(
                    GeneratedLine(
                        text=text,
                        validation_status="unvalidated",
                        validation_note=f"Urdu Arooz scan note: {exc}",
                    )
                )
    elif language == "bn":
        from app.meter.bengali.scanner import scan_bengali_line

        bengali_tmpl_map = {
            "aksharbritta": "payar",
            "matrabritta": "matrabritta_14",
            "swarobritta": "swarabritta_basic",
        }
        tmpl_key = bengali_tmpl_map.get(form, "payar")

        for text in lines:
            try:
                bn_scan = scan_bengali_line(text, tmpl_key)
                val_status = (
                    "matched"
                    if bn_scan.status == "matched"
                    else (
                        "over"
                        if bn_scan.status == "over"
                        else ("under" if bn_scan.status == "under" else "unvalidated")
                    )
                )
                result.append(
                    GeneratedLine(
                        text=text,
                        matra_count=bn_scan.count_value,
                        validation_status=val_status,  # type: ignore[arg-type]
                        validation_note=bn_scan.diagnostic_message,
                    )
                )
            except Exception as exc:
                result.append(
                    GeneratedLine(
                        text=text,
                        validation_status="unvalidated",
                        validation_note=f"Bengali scan note: {exc}",
                    )
                )
    else:
        # Hindi free verse or unconstrained
        for text in lines:
            result.append(
                GeneratedLine(
                    text=text,
                    validation_status="unvalidated",
                    validation_note="Free verse — no strict meter target applied.",
                )
            )

    return result
