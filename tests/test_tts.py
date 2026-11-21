"""Tests for Text-to-Speech recitation and audio processing."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.errors import GeminiNotConfiguredError
from app.tts.audio import pcm_to_wav, validate_wav, wav_duration_seconds
from app.tts.gemini import get_available_voices, get_recitation_styles, synthesize_line
from app.tts.languages import get_tts_lang_code, get_tts_status, is_tts_supported


def test_pcm_to_wav_and_validate():
    # 24000 samples of 16-bit silence (1 second)
    sample_rate = 24000
    pcm = b"\x00\x00" * sample_rate
    wav_bytes = pcm_to_wav(pcm, sample_rate=sample_rate, channels=1, sampwidth=2)

    assert validate_wav(wav_bytes) is True
    assert validate_wav(b"not a valid wav") is False
    assert validate_wav(b"") is False

    dur = wav_duration_seconds(wav_bytes)
    assert abs(dur - 1.0) < 0.05


def test_tts_languages_helpers():
    assert is_tts_supported("hi") is True
    assert is_tts_supported("bn") is True
    assert is_tts_supported("ur") is True
    assert is_tts_supported("unsupported_xyz") is False

    assert get_tts_lang_code("hi") == "hi-IN"
    assert get_tts_lang_code("bn") == "bn-IN"
    assert get_tts_lang_code("ur") == "ur-PK"

    assert get_tts_status("hi") == "supported"
    assert get_tts_status("bn") == "supported"
    assert get_tts_status("ur") == "experimental"
    assert get_tts_status("xyz") == "unsupported"


def test_tts_voices_and_styles():
    voices = get_available_voices()
    assert len(voices) >= 4
    assert any(v["id"] == "Kore" for v in voices)

    styles = get_recitation_styles()
    assert len(styles) >= 5
    assert "natural poetry recitation" in styles


@pytest.mark.asyncio
async def test_synthesize_line_validation_errors():
    with pytest.raises(ValueError, match="empty text"):
        await synthesize_line("")

    with pytest.raises(ValueError, match="exceeds maximum"):
        await synthesize_line("क" * 501)

    with pytest.raises(ValueError, match="Unsupported language"):
        await synthesize_line("कुछ पंक्तियाँ", language="latin_xyz")


@pytest.mark.asyncio
async def test_synthesize_line_unconfigured(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    with pytest.raises(GeminiNotConfiguredError):
        await synthesize_line("मन का दीपक जब जले", language="hi")


def test_tts_api_catalog_endpoints(test_client: TestClient):
    res_v = test_client.get("/api/tts/voices")
    assert res_v.status_code == 200
    assert "voices" in res_v.json()

    res_s = test_client.get("/api/tts/styles")
    assert res_s.status_code == 200
    assert "styles" in res_s.json()

    res_l = test_client.get("/api/tts/languages")
    assert res_l.status_code == 200
    assert "languages" in res_l.json()


def test_tts_api_endpoint_success(test_client: TestClient):
    dummy_pcm = b"\x00\x00" * 2400
    dummy_wav = pcm_to_wav(dummy_pcm)

    with patch("app.api.tts.synthesize_line", new_callable=AsyncMock) as mock_synth:
        mock_synth.return_value = dummy_wav

        payload = {
            "text": "मन का दीपक जब जले",
            "language": "hi",
            "voice": "Kore",
            "style": "natural poetry recitation",
        }
        res = test_client.post("/api/tts", json=payload)
        assert res.status_code == 200
        assert res.headers["content-type"] == "audio/wav"
        assert len(res.content) > 44


def test_tts_api_endpoint_experimental_warning(test_client: TestClient):
    dummy_pcm = b"\x00\x00" * 2400
    dummy_wav = pcm_to_wav(dummy_pcm)

    with patch("app.api.tts.synthesize_line", new_callable=AsyncMock) as mock_synth:
        mock_synth.return_value = dummy_wav

        payload = {
            "text": "دل ناداں تجھے ہوا کیا ہے",
            "language": "ur",
            "voice": "Charon",
            "style": "calm and expressive",
        }
        res = test_client.post("/api/tts", json=payload)
        assert res.status_code == 200
        assert "X-TTS-Warning" in res.headers
