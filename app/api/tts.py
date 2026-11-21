"""Text-to-Speech recitation API endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.errors import (
    GeminiAuthError,
    GeminiNotConfiguredError,
    GeminiProviderError,
    GeminiRateLimitError,
    GeminiTimeoutError,
)
from app.tts.gemini import get_available_voices, get_recitation_styles, synthesize_line
from app.tts.languages import SUPPORTED_LANGUAGES, get_tts_status

router = APIRouter(tags=["TTS"])


class TTSRequestPayload(BaseModel):
    """Payload for text-to-speech synthesis."""

    text: str = Field(..., min_length=1, max_length=500, description="Poetic line to synthesize")
    language: str = Field(default="hi", description="BCP-47 language code: 'hi', 'ur', 'bn'")
    voice: str = Field(default="Kore", description="Voice identifier")
    style: str = Field(default="natural poetry recitation", description="Recitation style")


@router.post("/tts")
async def synthesize_speech_endpoint(payload: TTSRequestPayload) -> Response:
    """
    Synthesize a single poetic line into WAV audio using Gemini TTS.
    Returns 16-bit 24kHz mono WAV audio stream.
    """
    try:
        audio_bytes = await synthesize_line(
            text=payload.text,
            language=payload.language,
            voice=payload.voice,
            style=payload.style,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except GeminiNotConfiguredError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "TTS_NOT_CONFIGURED", "message": str(exc)},
        ) from exc
    except GeminiAuthError as exc:
        raise HTTPException(
            status_code=401,
            detail={"code": "TTS_AUTH_ERROR", "message": str(exc)},
        ) from exc
    except GeminiRateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail={"code": "TTS_RATE_LIMIT", "message": str(exc)},
        ) from exc
    except GeminiTimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail={"code": "TTS_TIMEOUT", "message": str(exc)},
        ) from exc
    except GeminiProviderError as exc:
        raise HTTPException(
            status_code=502,
            detail={"code": "TTS_PROVIDER_ERROR", "message": str(exc)},
        ) from exc

    headers = {"Content-Disposition": "inline; filename=recitation.wav"}
    if get_tts_status(payload.language) == "experimental":
        headers["X-TTS-Warning"] = f"TTS for language '{payload.language}' is experimental."

    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers=headers,
    )


@router.get("/tts/voices")
async def list_voices_endpoint():
    """Return available Gemini TTS voices."""
    return {"voices": get_available_voices()}


@router.get("/tts/styles")
async def list_styles_endpoint():
    """Return available poetry recitation styles."""
    return {"styles": get_recitation_styles()}


@router.get("/tts/languages")
async def list_languages_endpoint():
    """Return TTS language support matrix."""
    return {"languages": SUPPORTED_LANGUAGES}
