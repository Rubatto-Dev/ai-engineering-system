from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_AGENT_TRAINING_CONFIG: dict[str, Any] = {
    "version": "1.0.0",
    "history_file": "docs/audits/agent_score_history.jsonl",
    "leaderboard_file": "docs/audits/agent_leaderboard.json",
    "shadow_report_file": "docs/audits/shadow_mode_report.json",
    "weights": {
        "execution_success": 0.30,
        "stage_validation": 0.25,
        "handoff_quality": 0.20,
        "audit_success": 0.15,
        "artifact_coverage": 0.10,
    },
    "thresholds": {
        "promotion_score": 0.90,
        "watch_score": 0.85,
        "min_runs_for_promotion": 3,
    },
    "leaderboard": {
        "window_days": 30,
        "min_runs": 2,
    },
    "shadow_mode": {
        "enabled": True,
        "mode": "autopilot_full",
        "profile": "shadow_autopilot_full",
    },
}


def load_agent_training_config(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "config" / "agent_training.json"
    merged = json.loads(json.dumps(DEFAULT_AGENT_TRAINING_CONFIG))
    if not path.exists():
        return merged

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return merged

    if not isinstance(payload, dict):
        return merged

    merged["version"] = str(payload.get("version", merged["version"]))
    for key in ["history_file", "leaderboard_file", "shadow_report_file"]:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            merged[key] = value.strip()

    for key in ["weights", "thresholds", "leaderboard", "shadow_mode"]:
        section = payload.get(key)
        if isinstance(section, dict):
            merged[key].update(section)

    return merged


def build_score_history_entry(
    *,
    project: str,
    cycle: int,
    mode: str,
    profile: str,
    is_shadow: bool,
    execution_result: dict[str, Any],
    audit_result: dict[str, Any] | None,
    weights: dict[str, float],
) -> dict[str, Any]:
    metrics = extract_score_metrics(execution_result, audit_result)
    normalized_weights = _normalize_weights(weights)
    score_global = 0.0
    for key, weight in normalized_weights.items():
        score_global += float(metrics.get(key, 0.0)) * weight

    stages = execution_result.get("stages", [])
    decision = _extract_decision(stages)
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "project": project,
        "cycle": cycle,
        "mode": mode,
        "profile": profile,
        "is_shadow": bool(is_shadow),
        "decision": decision,
        "execution_status": str(execution_result.get("status", "failed")),
        "audit_status": str(audit_result.get("status", "audit_failed")) if isinstance(audit_result, dict) else "audit_missing",
        "metrics": metrics,
        "weights": normalized_weights,
        "score_global": round(score_global, 4),
    }


def extract_score_metrics(execution_result: dict[str, Any], audit_result: dict[str, Any] | None) -> dict[str, float]:
    status = str(execution_result.get("status", "failed"))
    stages = execution_result.get("stages", [])
    stage_list = [item for item in stages if isinstance(item, dict)] if isinstance(stages, list) else []
    total_stages = len(stage_list)

    stage_validation_passed = 0
    handoff_packet_passed = 0
    for stage in stage_list:
        checks = stage.get("checks", {})
        if not isinstance(checks, dict):
            continue
        if checks.get("stage_validation_ok") is True:
            stage_validation_passed += 1
        if checks.get("handoff_packet_ok") is True:
            handoff_packet_passed += 1

    stage_validation_rate = (stage_validation_passed / total_stages) if total_stages else 0.0
    handoff_quality_rate = (handoff_packet_passed / total_stages) if total_stages else 0.0

    artifacts = execution_result.get("artifacts", [])
    artifact_list = [str(item) for item in artifacts if isinstance(item, str)] if isinstance(artifacts, list) else []
    core_docs = {
        "docs/26_proposta_avaliacao.md",
        "docs/28_validacao_pre_kickoff.md",
        "docs/31_politica_decisao_comercial.md",
    }
    normalized_artifacts = {_normalize_artifact_path(item) for item in artifact_list}
    found_docs = set()
    for expected in core_docs:
        expected_norm = expected.replace("\\", "/").lower()
        if expected_norm in normalized_artifacts:
            found_docs.add(expected)
            continue
        for artifact in normalized_artifacts:
            if artifact.endswith(expected_norm):
                found_docs.add(expected)
                break
    artifact_coverage = (len(found_docs) / len(core_docs)) if core_docs else 0.0

    audit_success = 0.0
    if isinstance(audit_result, dict) and str(audit_result.get("status")) == "audit_ok":
        audit_success = 1.0

    return {
        "execution_success": 1.0 if status == "success" else 0.0,
        "stage_validation": round(stage_validation_rate, 4),
        "handoff_quality": round(handoff_quality_rate, 4),
        "audit_success": round(audit_success, 4),
        "artifact_coverage": round(artifact_coverage, 4),
    }


def append_score_history(repo_root: Path, entry: dict[str, Any], history_file: str) -> str:
    path = repo_root / history_file
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return str(path)


def load_score_history(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def build_leaderboard_report(
    *,
    records: list[dict[str, Any]],
    window_days: int,
    min_runs: int,
    promotion_score: float,
    watch_score: float,
) -> dict[str, Any]:
    filtered = _filter_records_by_window(records, window_days)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in filtered:
        profile = str(record.get("profile", "unknown")).strip() or "unknown"
        grouped[profile].append(record)

    leaderboard: list[dict[str, Any]] = []
    for profile, entries in grouped.items():
        runs = len(entries)
        scores = [_as_float(item.get("score_global"), 0.0) for item in entries]
        metrics = [item.get("metrics", {}) if isinstance(item.get("metrics"), dict) else {} for item in entries]
        execution_rates = [_as_float(metric.get("execution_success"), 0.0) for metric in metrics]
        audit_rates = [_as_float(metric.get("audit_success"), 0.0) for metric in metrics]
        stage_rates = [_as_float(metric.get("stage_validation"), 0.0) for metric in metrics]
        handoff_rates = [_as_float(metric.get("handoff_quality"), 0.0) for metric in metrics]
        artifact_rates = [_as_float(metric.get("artifact_coverage"), 0.0) for metric in metrics]
        decisions = Counter(str(item.get("decision", "UNKNOWN")) for item in entries)

        avg_score = _avg(scores)
        entry = {
            "profile": profile,
            "runs": runs,
            "avg_score": round(avg_score, 4),
            "max_score": round(max(scores) if scores else 0.0, 4),
            "min_score": round(min(scores) if scores else 0.0, 4),
            "execution_success_rate": round(_avg(execution_rates), 4),
            "audit_success_rate": round(_avg(audit_rates), 4),
            "stage_validation_rate": round(_avg(stage_rates), 4),
            "handoff_quality_rate": round(_avg(handoff_rates), 4),
            "artifact_coverage_rate": round(_avg(artifact_rates), 4),
            "decision_distribution": dict(decisions),
            "eligible_for_promotion": runs >= min_runs,
            "recommended_action": _recommended_action(
                avg_score=avg_score,
                runs=runs,
                min_runs=min_runs,
                execution_success_rate=_avg(execution_rates),
                audit_success_rate=_avg(audit_rates),
                promotion_score=promotion_score,
                watch_score=watch_score,
            ),
        }
        leaderboard.append(entry)

    leaderboard.sort(
        key=lambda item: (
            _as_float(item.get("avg_score"), 0.0),
            _as_float(item.get("execution_success_rate"), 0.0),
            _as_float(item.get("audit_success_rate"), 0.0),
            _as_float(item.get("runs"), 0.0),
        ),
        reverse=True,
    )

    top_profile = leaderboard[0]["profile"] if leaderboard else None
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_days": window_days,
        "records_total": len(records),
        "records_in_window": len(filtered),
        "min_runs": min_runs,
        "promotion_score": promotion_score,
        "watch_score": watch_score,
        "top_profile": top_profile,
        "profiles": leaderboard,
    }


def compare_shadow_runs(primary_entry: dict[str, Any], shadow_entry: dict[str, Any]) -> dict[str, Any]:
    primary_score = _as_float(primary_entry.get("score_global"), 0.0)
    shadow_score = _as_float(shadow_entry.get("score_global"), 0.0)
    winner = "tie"
    if primary_score > shadow_score:
        winner = "primary"
    elif shadow_score > primary_score:
        winner = "shadow"

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "winner": winner,
        "score_delta": round(shadow_score - primary_score, 4),
        "decision_changed": str(primary_entry.get("decision")) != str(shadow_entry.get("decision")),
        "primary": {
            "profile": primary_entry.get("profile"),
            "mode": primary_entry.get("mode"),
            "decision": primary_entry.get("decision"),
            "score_global": primary_score,
            "metrics": primary_entry.get("metrics", {}),
        },
        "shadow": {
            "profile": shadow_entry.get("profile"),
            "mode": shadow_entry.get("mode"),
            "decision": shadow_entry.get("decision"),
            "score_global": shadow_score,
            "metrics": shadow_entry.get("metrics", {}),
        },
    }


def write_json_report(repo_root: Path, relative_path: str, payload: dict[str, Any]) -> str:
    target = repo_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(target)


def _normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    expected = ["execution_success", "stage_validation", "handoff_quality", "audit_success", "artifact_coverage"]
    raw = {key: _as_float(weights.get(key), 0.0) for key in expected}
    total = sum(raw.values())
    if total <= 0:
        return {key: 1.0 / len(expected) for key in expected}
    return {key: value / total for key, value in raw.items()}


def _extract_decision(stages: Any) -> str:
    if not isinstance(stages, list):
        return "UNKNOWN"
    for stage in stages:
        if not isinstance(stage, dict):
            continue
        if str(stage.get("agent_id")) != "00":
            continue
        checks = stage.get("checks", {})
        if isinstance(checks, dict):
            value = checks.get("decision")
            if isinstance(value, str) and value.strip():
                return value.strip()
    return "UNKNOWN"


def _filter_records_by_window(records: list[dict[str, Any]], window_days: int) -> list[dict[str, Any]]:
    if window_days <= 0:
        return list(records)
    now = datetime.now(timezone.utc)
    filtered: list[dict[str, Any]] = []
    for record in records:
        timestamp = _parse_iso_timestamp(record.get("timestamp_utc"))
        if timestamp is None:
            continue
        age_days = (now - timestamp).total_seconds() / 86400.0
        if age_days <= float(window_days):
            filtered.append(record)
    return filtered


def _recommended_action(
    *,
    avg_score: float,
    runs: int,
    min_runs: int,
    execution_success_rate: float,
    audit_success_rate: float,
    promotion_score: float,
    watch_score: float,
) -> str:
    if runs >= min_runs and avg_score >= promotion_score and execution_success_rate >= 0.99 and audit_success_rate >= 0.99:
        return "promote"
    if avg_score < watch_score or execution_success_rate < 0.90 or audit_success_rate < 0.90:
        return "rebaseline"
    return "monitor"


def _parse_iso_timestamp(raw: Any) -> datetime | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _normalize_artifact_path(path: str) -> str:
    return path.replace("\\", "/").strip().lower()
