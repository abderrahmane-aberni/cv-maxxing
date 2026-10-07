"""Hand-checked eval harness for Resolve's Gemini pipeline.

This is NOT a rigorous benchmark -- it's a handful of hand-picked CV/JD
pairs with a human-judged *range* the ATS score should fall in, run
against the real Gemini API. It exists to catch regressions (a prompt
change that suddenly scores everyone 90+, say) and to document, concretely,
what "reasonable" output looks like for this project.

Costs a few real Gemini calls to run (free on the free tier). Run from the
repo root using the backend's venv, e.g. on Windows:
    backend\\.venv\\Scripts\\python.exe tests\\eval\\run_eval.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from eval_cases import CASES  # noqa: E402
from app.gemini_client import GeminiOutputError, analyze  # noqa: E402


def main() -> None:
    results = []
    print(f"Running {len(CASES)} eval cases against the live Gemini API...\n")

    for case in CASES:
        low, high = case.expected_score_range
        try:
            result, usage = analyze(case.cv_text, case.job_description)
        except GeminiOutputError as exc:
            print(f"[ERROR] {case.name}: {exc}")
            results.append({"name": case.name, "error": str(exc)})
            continue

        score = result.ats_match_score
        passed = low <= score <= high
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {case.name}: score={score} expected={low}-{high}")
        print(f"         {case.rationale}")
        print(f"         tokens: in={usage.input_tokens} out={usage.output_tokens}\n")

        results.append(
            {
                "name": case.name,
                "score": score,
                "expected_range": [low, high],
                "passed": passed,
                "summary": result.summary,
            }
        )

    out_path = Path(__file__).resolve().parent / "results.json"
    out_path.write_text(
        json.dumps(
            {"run_at": datetime.now(timezone.utc).isoformat(), "results": results},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Results written to {out_path}")


if __name__ == "__main__":
    main()
