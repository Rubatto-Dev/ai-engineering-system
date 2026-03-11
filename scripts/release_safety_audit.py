from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_engineering_os.release_safety import run_release_safety_audit


def main() -> int:
    parser = argparse.ArgumentParser(description="Run release safety audit and persist report.")
    parser.add_argument(
        "--output",
        default="docs/audits/release_safety_report.json",
        help="Output JSON report path relative to repo root.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    report = run_release_safety_audit(repo_root)

    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"report_path={output_path}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
