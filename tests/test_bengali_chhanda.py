"""Tests for Bengali Chhanda prosody, Aksharbritta, Matrabritta, and Swarabritta."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.meter.bengali.aksharbritta import scan_aksharbritta
from app.meter.bengali.characters import (
    classify_char,
    is_consonant,
    is_hasanta,
    is_independent_vowel,
    is_vowel_sign,
)
from app.meter.bengali.matrabritta import scan_matrabritta
from app.meter.bengali.normalize import normalize_bengali
from app.meter.bengali.scanner import scan_bengali_line
from app.meter.bengali.swarabritta import scan_swarabritta, swarabritta_count
from app.meter.bengali.syllables import syllabify_bengali
from app.meter.bengali.templates import (
    get_bengali_template,
    list_bengali_templates,
)


def test_bengali_characters():
    assert is_independent_vowel("অ") is True
    assert is_independent_vowel("আ") is True
    assert is_consonant("ক") is True
    assert is_consonant("ম") is True
    assert is_vowel_sign("\u09be") is True  # া
    assert is_vowel_sign("\u09bf") is True  # ি
    assert is_hasanta("\u09cd") is True
    assert classify_char("অ") == "vowel"
    assert classify_char("ক") == "consonant"
    assert classify_char("\u09cd") == "hasanta"


def test_bengali_normalization():
    text = "মহাভারতের কথা"
    assert normalize_bengali(text) == text


def test_bengali_syllabification():
    sylls = syllabify_bengali("মহাভারতের কথা")
    # ম (1), হা (2), ভা (3), র (4), তের (5 or তে+র), ক (6), থা (7)
    assert len(sylls) >= 6
    assert all(s.source_end > s.source_start for s in sylls)


def test_aksharbritta_payar():
    line = "মহাভারতের কথা অমৃত সমান"
    res = scan_aksharbritta(line, target_count=14)
    assert res["count"] == 14
    assert res["status"] == "matched"
    assert len(res["break_positions"]) == 1


def test_matrabritta():
    line = "নীল নবঘনে আষাঢ় গগনে"
    res = scan_matrabritta(line, target_matras=12)
    assert res["count"] == 12
    assert res["status"] == "matched"


def test_swarabritta():
    line = "বৃষ্টি পড়ে টাপুর টুপুর"
    count = swarabritta_count(line)
    res = scan_swarabritta(line, target_pulses=8)
    assert count == 8
    assert res["status"] == "matched"


def test_bengali_templates_catalog():
    templates = list_bengali_templates()
    assert len(templates) >= 4
    assert get_bengali_template("payar") is not None
    assert get_bengali_template("matrabritta_14") is not None
    assert get_bengali_template("swarabritta_basic") is not None


def test_scan_bengali_line():
    line = "মহাভারতের কথা অমৃত সমান"
    scan = scan_bengali_line(line, "payar")
    assert scan.count_value == 14
    assert scan.status == "matched"
    assert scan.system == "aksharbritta"
    assert scan.count_unit == "aksharas"


def test_bengali_golden_datasets():
    data_dir = Path(__file__).resolve().parent.parent / "data" / "bengali"
    akshar_path = data_dir / "aksharbritta.json"
    broken_path = data_dir / "broken_examples.json"

    assert akshar_path.exists()
    assert broken_path.exists()

    with open(akshar_path, encoding="utf-8") as f:
        akshar_data = json.load(f)
        assert len(akshar_data) >= 3
        for item in akshar_data:
            assert "text" in item
            assert "source" in item

    with open(broken_path, encoding="utf-8") as f:
        broken_data = json.load(f)
        assert len(broken_data) >= 3
        for item in broken_data:
            res = scan_bengali_line(item["text"], item["intended_meter"])
            assert res.status == item["expected_status"]


def test_bengali_api_endpoint(test_client: TestClient):
    payload = {"text": "মহাভারতের কথা অমৃত সমান", "template": "payar"}
    res = test_client.post("/api/analyze/bengali", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["count_value"] == 14
    assert data["status"] == "matched"
    assert data["count_unit"] == "aksharas"
