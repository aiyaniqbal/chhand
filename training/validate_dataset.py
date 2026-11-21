"""Validate dataset integrity, schema compliance, and provenance metadata."""

import argparse
import json
from pathlib import Path


def validate_file(path: Path) -> tuple[bool, int, list[str]]:
    """
    Validate all JSONL records in a dataset file.
    Returns (is_valid, record_count, list_of_errors).
    """
    if not path.exists():
        return False, 0, [f"File does not exist: {path}"]

    errors = []
    count = 0
    seen_texts = set()

    required_top = {"language", "script", "task", "input", "expected_output", "provenance"}
    valid_languages = {"hi", "ur", "bn"}

    with open(path, encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            count += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"Line {idx}: Malformed JSON - {exc}")
                continue

            # Check top-level fields
            missing = required_top - set(rec.keys())
            if missing:
                errors.append(f"Line {idx}: Missing required fields: {missing}")

            lang = rec.get("language")
            if lang not in valid_languages:
                errors.append(f"Line {idx}: Unsupported language code '{lang}'")

            # Check provenance
            prov = rec.get("provenance", {})
            if not prov.get("author"):
                errors.append(f"Line {idx}: Missing author in provenance")
            if not prov.get("source"):
                errors.append(f"Line {idx}: Missing source in provenance")
            if not prov.get("license"):
                errors.append(f"Line {idx}: Missing license in provenance")

            # Check expected output
            out = rec.get("expected_output", {})
            out_text = out.get("text", "").strip()
            if not out_text:
                errors.append(f"Line {idx}: Missing expected output text")

            # Check duplicates
            dup_key = (lang, out_text)
            if dup_key in seen_texts:
                errors.append(f"Line {idx}: Duplicate record detected for '{out_text}'")
            seen_texts.add(dup_key)

    is_valid = len(errors) == 0
    return is_valid, count, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Chhand fine-tuning JSONL datasets.")
    parser.add_argument("--path", required=True, help="Path to JSONL file to validate")
    args = parser.parse_args()

    p = Path(args.path)
    valid, num_records, errs = validate_file(p)
    print(f"Validation result for {p.name}: {'PASSED' if valid else 'FAILED'}")
    print(f"Total records: {num_records}")
    if errs:
        print(f"Errors encountered ({len(errs)}):")
        for e in errs[:10]:
            print(f"  - {e}")
        if len(errs) > 10:
            print(f"  ... and {len(errs) - 10} more.")
        exit(1)
    else:
        print("All records meet schema and provenance requirements.")
