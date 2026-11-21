"""Tests for professional lyric sheet export."""

from fastapi.testclient import TestClient

from app.export.formatting import (
    clean_poem_title,
    format_author_line,
    group_lines_into_stanzas,
    safe_filename,
)
from app.export.html_export import generate_html_export
from app.export.lyric_sheet import ExportOptions, generate_lyric_sheet
from app.export.text_export import generate_text_export


def test_export_formatting_helpers():
    assert clean_poem_title("") == "Untitled Poem"
    assert clean_poem_title("  नई सुबह  ") == "नई सुबह"

    assert format_author_line("कबीर") == "— कबीर"
    assert format_author_line("") == ""

    assert safe_filename("नई सुबह", "hi", "txt") == "poem_hi.txt" or "hi.txt" in safe_filename(
        "नई सुबह", "hi", "txt"
    )
    assert safe_filename("Morning Ghazal", "ur", "html") == "morning_ghazal_ur.html"

    lines = ["पंक्ति 1", "पंक्ति 2", "पंक्ति 3", "पंक्ति 4"]
    stanzas = group_lines_into_stanzas(lines, stanza_size=2)
    assert len(stanzas) == 2
    assert len(stanzas[0]) == 2


def test_text_export_hindi():
    lines = ["मन का दीपक जब जले", "मिटे अँधेरा दूर", "सीख सदा सच की रखो", "साथ रहेगा नूर"]
    opts = {
        "title": "ज्ञान दीप",
        "author": "कबीर दास",
        "meter": "doha",
        "language": "hi",
    }
    txt = generate_text_export(lines, opts)
    assert "ज्ञान दीप" in txt
    assert "कबीर दास" in txt
    assert "मन का दीपक जब जले" in txt
    assert "Meter: Doha" in txt


def test_html_export_urdu_rtl():
    lines = [
        "کوئی امید بر نہیں آتی",
        "کوئی صورت نظر نہیں آتی",
    ]
    opts = {
        "title": "امید",
        "author": "مرزا غالب",
        "meter": "hazaj",
        "language": "ur",
    }
    html_out = generate_html_export(lines, opts)
    assert 'dir="rtl"' in html_out
    assert 'lang="ur"' in html_out
    assert "Noto Nastaliq Urdu" in html_out
    assert "مرزا غالب" in html_out
    assert "کوئی امید بر نہیں آتی" in html_out
    assert "@media print" in html_out


def test_html_export_bengali():
    lines = [
        "মহাভারতের কথা অমৃত সমান",
        "কাশীরাম দাস কহে শুনে পুণ্যবান",
    ]
    opts = {
        "title": "মহাভারত বন্দনা",
        "author": "কাশীরাম দাস",
        "meter": "payar",
        "language": "bn",
    }
    html_out = generate_html_export(lines, opts)
    assert 'dir="ltr"' in html_out
    assert 'lang="bn"' in html_out
    assert "Noto Sans Bengali" in html_out
    assert "মহাভারতের কথা অমৃত সমান" in html_out


def test_generate_lyric_sheet_orchestration():
    lines = ["पंक्ति १", "पंक्ति २"]
    opts_txt = ExportOptions(title="शीर्षक", author="लेखक", language="hi", format="txt")
    content, media, fname = generate_lyric_sheet(lines, opts_txt)
    assert media == "text/plain; charset=utf-8"
    assert fname.endswith(".txt")
    assert "पंक्ति १" in content

    opts_html = ExportOptions(title="शीर्षक", author="लेखक", language="hi", format="html")
    content_h, media_h, fname_h = generate_lyric_sheet(lines, opts_html)
    assert media_h == "text/html; charset=utf-8"
    assert fname_h.endswith(".html")
    assert "<!DOCTYPE html>" in content_h


def test_export_api_endpoints(test_client: TestClient):
    # Success TXT
    payload_txt = {
        "lines": ["मन का दीपक जब जले", "मिटे अँधेरा दूर"],
        "title": "ज्ञान दीप",
        "author": "कबीर",
        "language": "hi",
        "format": "txt",
    }
    res_txt = test_client.post("/api/export", json=payload_txt)
    assert res_txt.status_code == 200
    assert "text/plain" in res_txt.headers["content-type"]
    assert "ज्ञान दीप" in res_txt.text

    # Success HTML
    payload_html = {
        "lines": ["کوئی امید بر نہیں آتی", "کوئی صورت نظر نہیں آتی"],
        "title": "غزل",
        "language": "ur",
        "format": "html",
    }
    res_html = test_client.post("/api/export", json=payload_html)
    assert res_html.status_code == 200
    assert "text/html" in res_html.headers["content-type"]
    assert 'dir="rtl"' in res_html.text

    # Validation failure: empty lines
    res_empty = test_client.post("/api/export", json={"lines": []})
    assert res_empty.status_code == 422
