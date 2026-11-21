"""Gemini Text-to-Speech poetry recitation synthesis."""

import asyncio
import logging
from typing import Any

from google import genai

from app.config import settings
from app.errors import GeminiNotConfiguredError, GeminiProviderError, GeminiTimeoutError
from app.tts.audio import pcm_to_wav, validate_wav
from app.tts.languages import SUPPORTED_LANGUAGES, get_tts_lang_code

logger = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 500

VOICES = [
    {"id": "Kore", "name": "Kore", "description": "Warm, expressive and poetic tone"},
    {
        "id": "Charon",
        "name": "Charon",
        "description": "Clear narrative voice with measured cadence",
    },
    {"id": "Fenrir", "name": "Fenrir", "description": "Deep resonant voice for dramatic verses"},
    {"id": "Aoede", "name": "Aoede", "description": "Lyrical, melodic voice for rhymed meters"},
]

RECITATION_STYLES = [
    "natural poetry recitation",
    "calm and expressive",
    "storytelling",
    "devotional",
    "emotional",
    "dramatic",
    "slow and clear",
]


def get_available_voices() -> list[dict[str, str]]:
    """Return available prebuilt Gemini TTS voices."""
    return VOICES


def get_recitation_styles() -> list[str]:
    """Return supported poetry recitation styles."""
    return RECITATION_STYLES


def _extract_audio_bytes(response: Any) -> bytes | None:
    """Extract raw audio byte payload from Gemini GenerateContentResponse."""
    try:
        candidates = getattr(response, "candidates", None) or []
        for cand in candidates:
            content = getattr(cand, "content", None)
            parts = getattr(content, "parts", None) or []
            for part in parts:
                inline_data = getattr(part, "inline_data", None)
                if inline_data:
                    data = getattr(inline_data, "data", None)
                    if data:
                        return data
    except Exception as exc:
        logger.warning("Failed to extract audio bytes from response: %s", exc)
    return None


async def synthesize_line(
    text: str,
    language: str = "hi",
    voice: str = "Kore",
    style: str = "natural poetry recitation",
) -> bytes:
    """
    Synthesize a single poetic line into WAV audio using Gemini TTS.
    Returns standard 16-bit 24kHz mono WAV bytes.
    """
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Cannot synthesize speech for empty text.")
    if len(clean_text) > MAX_TEXT_LENGTH:
        raise ValueError(
            f"Text length ({len(clean_text)}) exceeds maximum allowed ({MAX_TEXT_LENGTH} characters)."
        )

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}'. Supported: {list(SUPPORTED_LANGUAGES.keys())}"
        )

    if not settings.is_gemini_configured:
        raise GeminiNotConfiguredError("Gemini API key is required for Text-to-Speech recitation.")

    bcp47_code = get_tts_lang_code(language) or "hi-IN"
    tts_model = getattr(settings, "GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
    timeout = getattr(settings, "GEMINI_TTS_TIMEOUT_SECONDS", 60.0)

    # Style metadata instruction kept separate from actual recited text
    style_instruction = (
        f"You are a poetic voice synthesizer. Recite this verse in a {style} style. "
        f"Language: {bcp47_code}. Do not speak any introductory or concluding remarks."
    )

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options={"api_version": "v1beta"},
    )

    try:
        response = await asyncio.wait_for(
            client.aio.models.generate_content(
                model=tts_model,
                contents=clean_text,
                config=genai.types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=genai.types.SpeechConfig(
                        voice_config=genai.types.VoiceConfig(
                            prebuilt_voice_config=genai.types.PrebuiltVoiceConfig(
                                voice_name=voice,
                            )
                        )
                    ),
                    system_instruction=style_instruction,
                ),
            ),
            timeout=timeout,
        )
    except TimeoutError as err:
        raise GeminiTimeoutError(f"TTS synthesis timed out after {timeout} seconds.") from err
    except Exception as exc:
        raise GeminiProviderError(f"Gemini TTS synthesis failed: {exc}") from exc

    raw_audio = _extract_audio_bytes(response)
    if not raw_audio:
        raise GeminiProviderError("Gemini TTS response contained no audio data.")

    # Wrap raw PCM in standard WAV if not already formatted
    if validate_wav(raw_audio):
        return raw_audio

    return pcm_to_wav(raw_audio, sample_rate=24000, channels=1, sampwidth=2)
