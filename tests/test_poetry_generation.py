"""Tests for multilingual poetry generation and language registry."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.languages.registry import get_all_languages, get_language, is_supported
from app.poetry.generator import generate_poem
from app.poetry.prompts import build_bengali_prompt, build_hindi_prompt, build_urdu_prompt
from app.poetry.validator import validate_lines
from app.schemas import GenerateRequest


def test_language_registry():
    assert is_supported("hi") is True
    assert is_supported("ur") is True
    assert is_supported("bn") is True
    assert is_supported("es") is False

    hi = get_language("hi")
    assert hi is not None
    assert hi.script == "Devanagari"
    assert hi.direction == "ltr"
    assert "doha" in hi.poem_forms

    ur = get_language("ur")
    assert ur is not None
    assert ur.direction == "rtl"
    assert "ghazal" in ur.poem_forms

    all_langs = get_all_languages()
    assert len(all_langs) == 3


def test_prompt_builders():
    req_hi = GenerateRequest(language="hi", poem_form="doha", theme="nature")
    prompt_hi = build_hindi_prompt(req_hi)
    assert "Doha" in prompt_hi
    assert "nature" in prompt_hi

    req_ur = GenerateRequest(language="ur", poem_form="ghazal", theme="ishq")
    prompt_ur = build_urdu_prompt(req_ur)
    assert "Ghazal" in prompt_ur
    assert "ishq" in prompt_ur

    req_bn = GenerateRequest(language="bn", poem_form="aksharbritta", theme="rain")
    prompt_bn = build_bengali_prompt(req_bn)
    assert "Aksharbritta" in prompt_bn


def test_validator_hindi_doha():
    req = GenerateRequest(language="hi", poem_form="doha")
    lines = [
        "मन का दीपक जब जले",  # 13 matras (matched)
        "मिटे अँधेरा दूर",  # 11 matras (matched)
        "सीख सदा सच की रखो",  # 13 matras (matched)
        "साथ रहेगा नूर",  # 11 matras (matched)
    ]
    val_lines = validate_lines(lines, req)
    assert len(val_lines) == 4
    assert all(item.validation_status == "matched" for item in val_lines)


def test_validator_bengali_payar():
    req = GenerateRequest(language="bn", poem_form="aksharbritta")
    lines = [
        "মহাভারতের কথা অমৃত সমান",  # 14 aksharas (matched)
        "কাশীরাম দাস কহে শুনে পুণ্যবান",  # 14 aksharas (matched)
    ]
    val_lines = validate_lines(lines, req)
    assert len(val_lines) == 2
    assert all(item.validation_status == "matched" for item in val_lines)


@pytest.mark.asyncio
async def test_generate_poem_with_mock_client():
    mock_client = AsyncMock()
    mock_client.is_configured = True
    mock_client.model = "gemini-3.8-flash"
    mock_client.generate_structured_json.return_value = {
        "stanzas": [
            {
                "lines": [
                    {"text": "मन का दीपक जब जले"},
                    {"text": "मिटे अँधेरा दूर"},
                    {"text": "सीख सदा सच की रखो"},
                    {"text": "साथ रहेगा नूर"},
                ]
            }
        ]
    }

    req = GenerateRequest(language="hi", poem_form="doha", theme="hope")
    resp = await generate_poem(req, client=mock_client)

    assert resp.language == "hi"
    assert resp.poem_form == "doha"
    assert len(resp.stanzas) == 1
    assert len(resp.stanzas[0]) == 4
    assert resp.validation.status in ("verified", "partially_verified")
    assert resp.validation.meter_matches == 4


def test_api_languages_endpoint(test_client: TestClient):
    res = test_client.get("/api/languages")
    assert res.status_code == 200
    langs = res.json()
    assert len(langs) == 3
    codes = [entry["language_code"] for entry in langs]
    assert "hi" in codes
    assert "ur" in codes
    assert "bn" in codes


def test_api_generate_endpoint_with_mock(test_client: TestClient, monkeypatch):
    from app.api import generate
    from app.schemas import GeneratedLine, GenerateResponse, PoemValidation

    async def fake_generate(req):
        return GenerateResponse(
            language=req.language,
            poem_form=req.poem_form,
            stanzas=[[GeneratedLine(text="मन का दीपक जब जले", validation_status="matched")]],
            validation=PoemValidation(status="verified", meter_matches=1, total_units=1),
            model_used="gemini-3.8-flash",
            generation_note="Mock test generated",
        )

    monkeypatch.setattr(generate, "generate_poem", fake_generate)

    payload = {
        "language": "hi",
        "poem_form": "doha",
        "theme": "light",
    }
    res = test_client.post("/api/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["language"] == "hi"
    assert data["validation"]["status"] == "verified"
