from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_engineering_os.decision_calibration import calibrate_decision_policy


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrate segment decision thresholds from decision history.")
    parser.add_argument(
        "--output",
        default="docs/audits/decision_policy_calibration_report.json",
        help="Output JSON report path relative to repo root.",
    )
    parser.add_argument(
        "--write-policy",
        action="store_true",
        help="Apply calibrated thresholds into config/decision_policy.json.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    report = calibrate_decision_policy(repo_root, apply_updates=args.write_policy)

    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"report_path={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
