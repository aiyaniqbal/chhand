"""Poetry generator using Google Gemini and deterministic meter verification."""

import logging

from app.errors import GeminiNotConfiguredError
from app.llm.adaption import get_client_for_language
from app.llm.client import LLMClient
from app.poetry.prompts import (
    SYSTEM_PROMPTS,
    build_bengali_prompt,
    build_hindi_prompt,
    build_urdu_prompt,
)
from app.poetry.validator import validate_lines
from app.schemas import GeneratedLine, GenerateRequest, GenerateResponse, PoemValidation

logger = logging.getLogger(__name__)


async def generate_poem(
    request: GenerateRequest,
    client: LLMClient | None = None,
) -> GenerateResponse:
    """
    Generate original poetry in Hindi, Urdu, or Bengali.
    Calls Gemini for candidate generation, then validates using deterministic scanners.
    """
    llm = client or get_client_for_language(request.language)
    if not llm.is_configured:
        raise GeminiNotConfiguredError("Gemini API key is required for poetry generation.")

    system_instruction = SYSTEM_PROMPTS.get(request.language, SYSTEM_PROMPTS["hi"])

    if request.language == "hi":
        user_prompt = build_hindi_prompt(request)
    elif request.language == "ur":
        user_prompt = build_urdu_prompt(request)
    elif request.language == "bn":
        user_prompt = build_bengali_prompt(request)
    else:
        user_prompt = build_hindi_prompt(request)

    data = await llm.generate_structured_json(
        prompt=user_prompt,
        system_instruction=system_instruction,
    )

    raw_stanzas = data.get("stanzas", [])
    if not raw_stanzas:
        raw_lines = data.get("lines", [])
        if raw_lines:
            raw_stanzas = [{"lines": raw_lines}]
        else:
            raw_stanzas = []

    validated_stanzas: list[list[GeneratedLine]] = []
    all_validated_lines: list[GeneratedLine] = []

    for stanza_data in raw_stanzas:
        raw_lines_in_stanza = stanza_data.get("lines", [])
        line_texts: list[str] = []
        for line_item in raw_lines_in_stanza:
            if isinstance(line_item, dict):
                text_val = line_item.get("text", "").strip()
                if text_val:
                    line_texts.append(text_val)
            elif isinstance(line_item, str):
                text_val = line_item.strip()
                if text_val:
                    line_texts.append(text_val)

        val_lines = validate_lines(line_texts, request)
        validated_stanzas.append(val_lines)
        all_validated_lines.extend(val_lines)

    total_units = len(all_validated_lines)
    meter_matches = sum(1 for line in all_validated_lines if line.validation_status == "matched")

    if total_units == 0:
        val_status = "unvalidated"
    elif meter_matches == total_units and request.poem_form not in ("free_verse", "nazm"):
        val_status = "verified"
    elif meter_matches > 0:
        val_status = "partially_verified"
    else:
        val_status = "unvalidated"

    validation = PoemValidation(
        status=val_status,
        meter_matches=meter_matches,
        total_units=total_units,
    )

    return GenerateResponse(
        language=request.language,
        poem_form=request.poem_form,
        stanzas=validated_stanzas,
        validation=validation,
        model_used=llm.model,
        generation_note=f"Generated {len(validated_stanzas)} stanza(s) with {total_units} total line(s).",
    )
