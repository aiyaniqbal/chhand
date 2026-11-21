"""Language registry and capability API."""

from fastapi import APIRouter

from app.languages.registry import get_all_languages
from app.schemas import LanguageInfo

router = APIRouter(tags=["Languages"])


@router.get("/languages", response_model=list[LanguageInfo])
async def list_languages() -> list[LanguageInfo]:
    """Return capability descriptors for all supported languages."""
    caps = get_all_languages()
    return [
        LanguageInfo(
            language_code=cap.language_code,
            name=cap.name,
            native_name=cap.native_name,
            script=cap.script,
            direction=cap.direction,
            meter_systems=cap.meter_systems,
            poem_forms=cap.poem_forms,
            scanner_available=cap.scanner_available,
            rhyme_available=cap.rhyme_available,
            tts_status=cap.tts_status,
            export_available=cap.export_available,
            generator_available=cap.generator_available,
        )
        for cap in caps
    ]
