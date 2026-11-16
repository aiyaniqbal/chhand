"""Generate-and-Verify loop: LLM candidate generation + deterministic meter verification."""

from app.config import settings
from app.errors import LLMConfigurationError, LLMTimeoutError
from app.llm.client import LLMClient
from app.llm.prompts import build_rewrite_system_prompt, build_rewrite_user_prompt
from app.meter.scanner import scan_line
from app.rhyme.endings import are_rhymes
from app.schemas import RewriteRequest, RewriteResponse, Suggestion


async def generate_verified_suggestions(
    request: RewriteRequest,
    client: LLMClient | None = None,
) -> RewriteResponse:
    """
    Core AI workflow:
    1. Meter engine analyzes current broken line.
    2. LLM proposes candidate rewrites.
    3. Python meter engine scans every candidate.
    4. Failed candidates are discarded.
    5. Retries up to MAX_RETRIES until sufficient verified candidates are found.
    6. Returns ONLY deterministically verified lines.
    """
    llm = client or LLMClient()
    if not llm.is_configured:
        raise LLMConfigurationError(
            "LLM API key is not configured. AI rewriting requires LLM_API_KEY to be set in .env."
        )

    # 1. Deterministic baseline scan of the original line
    current_scan = scan_line(
        text=request.original_line,
        target_matras=request.target_matra_count,
        charan_index=request.charan_index,
        meter_name=request.selected_meter,
        pronunciation_mode=request.pronunciation_mode,
    )

    verified_suggestions: list[Suggestion] = []
    seen_lines: set[str] = {request.original_line.strip()}
    max_attempts = settings.MAX_RETRIES
    attempts_made = 0

    system_prompt = build_rewrite_system_prompt()
    user_prompt = build_rewrite_user_prompt(request, current_scan)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    while attempts_made < max_attempts and len(verified_suggestions) < request.max_suggestions:
        attempts_made += 1
        try:
            data = await llm.generate_json(
                messages,
                temperature=0.7
                + (0.1 * (attempts_made - 1)),  # slight temperature increase on retry
            )
        except (LLMTimeoutError, LLMConfigurationError):
            raise
        except Exception:
            if attempts_made >= max_attempts and not verified_suggestions:
                raise
            break

        candidates = data.get("candidates", [])
        for item in candidates:
            cand_text = (item.get("line") or "").strip()
            cand_note = (item.get("note") or "").strip()

            if not cand_text or cand_text in seen_lines:
                continue

            # 2. Strict Deterministic Meter Verification
            cand_scan = scan_line(
                text=cand_text,
                target_matras=request.target_matra_count,
                charan_index=request.charan_index,
                meter_name=request.selected_meter,
                pronunciation_mode=request.pronunciation_mode,
            )

            # Verification rule: MUST exactly match the required matra count
            if (
                cand_scan.status != "matched"
                or cand_scan.actual_matras != request.target_matra_count
            ):
                # REJECT: Meter condition violated
                continue

            # If phonetic mode detected unresolved pronunciation ambiguities, discard
            if cand_scan.status == "ambiguous":
                continue

            # 3. Optional rhyme check
            rhyme_compat = None
            if request.rhyme_requirement:
                rhyme_compat = are_rhymes(cand_text, request.rhyme_requirement)

            seen_lines.add(cand_text)
            verified_suggestions.append(
                Suggestion(
                    suggested_line=cand_text,
                    calculated_matra_count=cand_scan.actual_matras,
                    target_matra_count=request.target_matra_count,
                    verified_status=True,
                    rhyme_compatibility=rhyme_compat,
                    meaning_note=cand_note or "Matches target meter exactly.",
                    syllables=cand_scan.syllables,
                    verification_details={
                        "individual_weights": cand_scan.individual_weights,
                        "cumulative_weights": cand_scan.cumulative_weights,
                    },
                )
            )

            if len(verified_suggestions) >= request.max_suggestions:
                break

    if verified_suggestions:
        return RewriteResponse(
            suggestions=verified_suggestions[: request.max_suggestions],
            message=f"Found {len(verified_suggestions)} verified rewrite(s) matching {request.target_matra_count} matras.",
            attempts_made=attempts_made,
        )

    return RewriteResponse(
        suggestions=[],
        message="No verified rewrite found. Try changing the meaning or generating again.",
        attempts_made=attempts_made,
    )
