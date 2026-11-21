"""Tests for Urdu Arooz prosody, Bahr matching, and Taqti analysis."""

from fastapi.testclient import TestClient

from app.meter.urdu.bahr import get_bahr, list_bahrs
from app.meter.urdu.characters import is_consonant, is_diacritic, is_long_vowel
from app.meter.urdu.diacritics import extract_diacritics, has_diacritics, strip_diacritics
from app.meter.urdu.lexicon import lookup_word_pattern
from app.meter.urdu.normalize import normalize_urdu
from app.meter.urdu.qafiya import extract_qafiya, extract_radif
from app.meter.urdu.scanner import scan_urdu_line
from app.meter.urdu.syllables import syllabify_urdu


def test_character_classification():
    assert is_consonant("ب") is True
    assert is_consonant("م") is True
    assert is_consonant("ک") is True
    assert is_long_vowel("ا") is True
    assert is_long_vowel("و") is True
    assert is_long_vowel("ی") is True
    assert is_diacritic("\u064e") is True  # Zabar / Fatha
    assert is_diacritic("\u0650") is True  # Zer / Kasra
    assert is_diacritic("\u0652") is True  # Sukun


def test_normalization():
    # Arabic Yeh -> Urdu Chhoti Ye
    assert normalize_urdu("عربیي") == "عربیی"
    # Arabic Kaf -> Urdu Keheh
    assert normalize_urdu("كتاب") == "کتاب"
    # Preserves Do-chashmi He
    assert "ھ" in normalize_urdu("گھر")


def test_diacritics():
    vocalized = "دِلِ ناداں"
    assert has_diacritics(vocalized) is True
    assert has_diacritics("دل ناداں") is False
    assert strip_diacritics(vocalized) == "دل ناداں"
    extracted = extract_diacritics(vocalized)
    assert len(extracted) == 2


def test_lexicon():
    assert lookup_word_pattern("دل") == "L"
    assert lookup_word_pattern("محبت") == "SLL"
    assert lookup_word_pattern("غزل") == "SL"
    assert lookup_word_pattern("غیر_معروف_لفظ_xyz") is None


def test_syllabification():
    sylls = syllabify_urdu("دل ناداں")
    assert len(sylls) >= 2
    assert all(hasattr(s, "weight") for s in sylls)


def test_bahr_definitions():
    bahrs = list_bahrs()
    assert len(bahrs) >= 5
    assert get_bahr("hazaj_musamman") is not None
    assert get_bahr("ramal_musamman") is not None
    assert get_bahr("mutaqarib_musamman") is not None
    assert get_bahr("kamil_musaddas") is not None
    assert get_bahr("khafif_musaddas") is not None


def test_scan_urdu_line():
    line = "دل ناداں تجھے ہوا کیا ہے"
    res = scan_urdu_line(line)
    assert res.original_text == line
    assert len(res.words) == 6
    assert len(res.weight_pattern) > 0
    assert res.confidence > 0.0


def test_qafiya_and_radif():
    lines = [
        "کوئی امید بر نہیں آتی",
        "کوئی صورت نظر نہیں آتی",
    ]
    radif = extract_radif(lines)
    assert radif == "نہیں آتی"
    qafiya = extract_qafiya(lines)
    assert qafiya["radif"] == "نہیں آتی"
    assert "بر" in qafiya["rhyme_words"]
    assert "نظر" in qafiya["rhyme_words"]
    assert qafiya["is_consistent"] is True


def test_urdu_api_endpoint(test_client: TestClient):
    payload = {"text": "دل ناداں تجھے ہوا کیا ہے", "bahr": "hazaj_musamman"}
    res = test_client.post("/api/analyze/urdu", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "weight_pattern" in data
    assert data["original_text"] == payload["text"]
    assert "explanation" in data
