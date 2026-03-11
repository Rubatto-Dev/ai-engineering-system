from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from tempfile import mkdtemp
from typing import Any

from ai_engineering_os.agent_training import (
    append_score_history,
    build_leaderboard_report,
    build_score_history_entry,
    compare_shadow_runs,
    load_agent_training_config,
    load_score_history,
    write_json_report,
)
from ai_engineering_os.jarvis import JarvisEngine


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a full Jarvis cycle with optional shadow mode.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--cycle", type=int, default=1)
    parser.add_argument("--mode", default="autopilot_safe")
    parser.add_argument("--proposal-file", dest="proposal_file")
    parser.add_argument("--strict-external", action="store_true")
    parser.add_argument("--profile", default="primary")
    parser.add_argument("--shadow", action="store_true", help="Run challenger cycle in isolated workspace.")
    parser.add_argument("--shadow-mode", dest="shadow_mode")
    parser.add_argument("--shadow-profile", dest="shadow_profile")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    training_config = load_agent_training_config(repo_root)
    weights = _as_dict(training_config.get("weights"))
    history_file = str(training_config.get("history_file", "docs/audits/agent_score_history.jsonl"))
    leaderboard_file = str(training_config.get("leaderboard_file", "docs/audits/agent_leaderboard.json"))
    shadow_report_file = str(training_config.get("shadow_report_file", "docs/audits/shadow_mode_report.json"))
    thresholds_cfg = _as_dict(training_config.get("thresholds"))
    leaderboard_cfg = _as_dict(training_config.get("leaderboard"))
    shadow_cfg = _as_dict(training_config.get("shadow_mode"))

    primary_outputs = _run_cycle(
        repo_root=repo_root,
        project=args.project,
        cycle=args.cycle,
        mode=args.mode,
        proposal_file=args.proposal_file,
        strict_external=args.strict_external,
    )
    primary_exec = _extract_step_result(primary_outputs, 2)
    primary_audit = _extract_step_result(primary_outputs, 3)
    primary_entry = build_score_history_entry(
        project=args.project,
        cycle=args.cycle,
        mode=args.mode,
        profile=args.profile,
        is_shadow=False,
        execution_result=primary_exec,
        audit_result=primary_audit,
        weights={key: float(value) for key, value in weights.items()},
    )
    history_path = append_score_history(repo_root, primary_entry, history_file)

    shadow_outputs: list[dict[str, Any]] | None = None
    shadow_entry: dict[str, Any] | None = None
    shadow_report_path: str | None = None

    shadow_requested = bool(args.shadow) or bool(args.shadow_mode)
    if shadow_requested and bool(shadow_cfg.get("enabled", True)):
        shadow_mode = str(args.shadow_mode or shadow_cfg.get("mode", "autopilot_full"))
        shadow_profile = str(args.shadow_profile or shadow_cfg.get("profile", "shadow_autopilot_full"))
        shadow_outputs = _run_shadow_cycle(
            source_repo_root=repo_root,
            project=args.project,
            cycle=args.cycle,
            mode=shadow_mode,
            proposal_file=args.proposal_file,
            strict_external=args.strict_external,
        )
        shadow_exec = _extract_step_result(shadow_outputs, 2)
        shadow_audit = _extract_step_result(shadow_outputs, 3)
        shadow_entry = build_score_history_entry(
            project=args.project,
            cycle=args.cycle,
            mode=shadow_mode,
            profile=shadow_profile,
            is_shadow=True,
            execution_result=shadow_exec,
            audit_result=shadow_audit,
            weights={key: float(value) for key, value in weights.items()},
        )
        append_score_history(repo_root, shadow_entry, history_file)
        comparison = compare_shadow_runs(primary_entry, shadow_entry)
        shadow_report_path = write_json_report(repo_root, shadow_report_file, comparison)

    records = load_score_history(repo_root / history_file)
    window_days = int(leaderboard_cfg.get("window_days", 30))
    min_runs = int(leaderboard_cfg.get("min_runs", thresholds_cfg.get("min_runs_for_promotion", 2)))
    promotion_score = float(thresholds_cfg.get("promotion_score", 0.90))
    watch_score = float(thresholds_cfg.get("watch_score", 0.85))
    leaderboard_report = build_leaderboard_report(
        records=records,
        window_days=window_days,
        min_runs=min_runs,
        promotion_score=promotion_score,
        watch_score=watch_score,
    )
    leaderboard_report_path = write_json_report(repo_root, leaderboard_file, leaderboard_report)

    payload: dict[str, Any] = {
        "primary": primary_outputs,
        "shadow": shadow_outputs,
        "score_entries": [primary_entry] + ([shadow_entry] if isinstance(shadow_entry, dict) else []),
        "reports": {
            "score_history": history_path,
            "leaderboard": leaderboard_report_path,
            "shadow": shadow_report_path,
        },
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _run_cycle(
    *,
    repo_root: Path,
    project: str,
    cycle: int,
    mode: str,
    proposal_file: str | None,
    strict_external: bool,
) -> list[dict[str, Any]]:
    engine = JarvisEngine(repo_root)
    start_command = f"JARVIS: START project={project}"
    if proposal_file:
        start_command += f" proposal_file={proposal_file}"

    audit_command = "JARVIS: AUDIT repo=current tests_ok=true security_ok=true sonar_ok=true"
    if strict_external:
        audit_command += " strict_external=true"

    return [
        _as_dict(engine.handle(start_command)),
        _as_dict(engine.handle(f"JARVIS: PLAN cycle={cycle}")),
        _as_dict(engine.handle(f"JARVIS: EXEC cycle={cycle} mode={mode}")),
        _as_dict(engine.handle(audit_command)),
    ]


def _run_shadow_cycle(
    *,
    source_repo_root: Path,
    project: str,
    cycle: int,
    mode: str,
    proposal_file: str | None,
    strict_external: bool,
) -> list[dict[str, Any]]:
    temp_root = Path(mkdtemp(prefix="jarvis_shadow_"))
    shadow_root = temp_root / "workspace"
    try:
        shutil.copytree(
            source_repo_root,
            shadow_root,
            ignore=shutil.ignore_patterns(
                ".git",
                "node_modules",
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
            ),
        )
        return _run_cycle(
            repo_root=shadow_root,
            project=project,
            cycle=cycle,
            mode=mode,
            proposal_file=proposal_file,
            strict_external=strict_external,
        )
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def _extract_step_result(outputs: list[dict[str, Any]], index: int) -> dict[str, Any]:
    if index < 0 or index >= len(outputs):
        return {}
    item = outputs[index]
    return item if isinstance(item, dict) else {}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


if __name__ == "__main__":
    raise SystemExit(main())
