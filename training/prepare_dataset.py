"""Prepare and clean multilingual poetry fine-tuning datasets."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.meter.bengali.normalize import normalize_bengali
from app.meter.normalize import normalize_devanagari
from app.meter.urdu.normalize import normalize_urdu


def normalize_record_text(record: dict) -> dict:
    """Normalize text fields according to the record's language rules."""
    lang = record.get("language")
    in_text = record.get("input", {}).get("original_text", "")
    out_text = record.get("expected_output", {}).get("text", "")

    if lang == "hi":
        record["input"]["original_text"] = normalize_devanagari(in_text)
        record["expected_output"]["text"] = normalize_devanagari(out_text)
    elif lang == "ur":
        record["input"]["original_text"] = normalize_urdu(in_text)
        record["expected_output"]["text"] = normalize_urdu(out_text)
    elif lang == "bn":
        record["input"]["original_text"] = normalize_bengali(in_text)
        record["expected_output"]["text"] = normalize_bengali(out_text)

    return record


def prepare_file(input_path: Path, output_path: Path) -> int:
    """Read, clean, deduplicate, and write out normalized JSONL records."""
    if not input_path.exists():
        print(f"Error: {input_path} does not exist.")
        return 0

    seen_outputs = set()
    cleaned_records = []

    with open(input_path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"Line {line_num}: JSON syntax error: {exc}")
                continue

            rec = normalize_record_text(rec)
            out_key = (rec.get("language"), rec.get("expected_output", {}).get("text", "").strip())
            if out_key in seen_outputs:
                continue
            seen_outputs.add(out_key)
            cleaned_records.append(rec)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for rec in cleaned_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Successfully processed {len(cleaned_records)} unique records -> {output_path}")
    return len(cleaned_records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare Chhand poetry tuning datasets.")
    parser.add_argument("--input", required=True, help="Input JSONL path")
    parser.add_argument("--output", required=True, help="Output JSONL path")
    args = parser.parse_args()

    prepare_file(Path(args.input), Path(args.output))
