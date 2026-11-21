"""Evaluate fine-tuned or base poetry models using deterministic meter scanners."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.meter.bengali.scanner import scan_bengali_line
from app.meter.scanner import scan_line
from app.meter.urdu.scanner import scan_urdu_line


def evaluate_dataset(path: Path) -> dict:
    """
    Evaluate expected outputs in a dataset using the deterministic meter engines.
    Returns metrics on meter pass rates across languages.
    """
    if not path.exists():
        return {"error": f"Path not found: {path}"}

    total_records = 0
    passed_records = 0
    by_language: dict[str, dict[str, int]] = {
        "hi": {"total": 0, "passed": 0},
        "ur": {"total": 0, "passed": 0},
        "bn": {"total": 0, "passed": 0},
    }

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            lang = rec.get("language")
            meter = rec.get("input", {}).get("meter")
            out_text = rec.get("expected_output", {}).get("text", "")

            if lang not in by_language:
                continue

            total_records += 1
            by_language[lang]["total"] += 1
            matched = False

            if lang == "hi":
                # For Hindi Doha / Chaupai
                target = 13 if "13" in str(rec.get("input", {}).get("target_pattern", "")) else 16
                res = scan_line(out_text, target_matras=target)
                if res.status == "matched":
                    matched = True
            elif lang == "ur":
                res = scan_urdu_line(out_text, meter)
                if res.matched_bahr or res.confidence >= 0.7:
                    matched = True
            elif lang == "bn":
                tmpl = "payar" if "payar" in meter else "matrabritta_14"
                res = scan_bengali_line(out_text, tmpl)
                if res.status == "matched":
                    matched = True

            if matched:
                passed_records += 1
                by_language[lang]["passed"] += 1

    overall_accuracy = round(passed_records / total_records, 2) if total_records > 0 else 0.0

    return {
        "total_records": total_records,
        "passed_records": passed_records,
        "overall_accuracy": overall_accuracy,
        "by_language": by_language,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate poetry dataset meter adherence.")
    parser.add_argument("--path", required=True, help="Path to evaluation JSONL file")
    args = parser.parse_args()

    results = evaluate_dataset(Path(args.path))
    print("Evaluation Results:")
    print(json.dumps(results, indent=2))
