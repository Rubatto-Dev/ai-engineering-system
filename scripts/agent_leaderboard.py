from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_engineering_os.agent_training import (
    build_leaderboard_report,
    load_agent_training_config,
    load_score_history,
    write_json_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build automated leaderboard for agent profiles.")
    parser.add_argument("--history", help="Score history JSONL path relative to repo root.")
    parser.add_argument("--output", help="Leaderboard output JSON path relative to repo root.")
    parser.add_argument("--window-days", type=int, help="Window in days for leaderboard aggregation.")
    parser.add_argument("--min-runs", type=int, help="Minimum runs to be eligible for promotion.")
    parser.add_argument("--promotion-score", type=float, help="Minimum average score for promotion.")
    parser.add_argument("--watch-score", type=float, help="Watch threshold for rebaseline recommendation.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    config = load_agent_training_config(repo_root)

    history_file = str(args.history or config.get("history_file", "docs/audits/agent_score_history.jsonl"))
    output_file = str(args.output or config.get("leaderboard_file", "docs/audits/agent_leaderboard.json"))
    leaderboard_cfg = config.get("leaderboard", {})
    thresholds_cfg = config.get("thresholds", {})

    window_days = int(args.window_days or leaderboard_cfg.get("window_days", 30))
    min_runs = int(args.min_runs or leaderboard_cfg.get("min_runs", 2))
    promotion_score = float(args.promotion_score or thresholds_cfg.get("promotion_score", 0.90))
    watch_score = float(args.watch_score or thresholds_cfg.get("watch_score", 0.85))

    records = load_score_history(repo_root / history_file)
    report = build_leaderboard_report(
        records=records,
        window_days=window_days,
        min_runs=min_runs,
        promotion_score=promotion_score,
        watch_score=watch_score,
    )

    output_path = write_json_report(repo_root, output_file, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"report_path={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
