from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .decision_policy import (
    POLICY_FILE,
    PROJECT_SEGMENTS,
    REQUIRED_THRESHOLD_KEYS,
    load_decision_policy,
    resolve_thresholds_for_segment,
)


def calibrate_decision_policy(
    repo_root: Path,
    *,
    apply_updates: bool = False,
) -> dict[str, Any]:
    policy = load_decision_policy(repo_root)
    calibration_cfg = policy.get("calibration", {}) if isinstance(policy.get("calibration"), dict) else {}
    history_file = str(calibration_cfg.get("history_file", "docs/audits/proposal_decision_history.jsonl"))
    min_samples = max(1, _as_int(calibration_cfg.get("min_samples_per_segment"), 5))
    history_path = repo_root / history_file
    records = _load_history_records(history_path)

    segment_reports: dict[str, Any] = {}
    segment_thresholds: dict[str, Any] = {}
    used_any_history = False

    for segment in PROJECT_SEGMENTS:
        current = resolve_thresholds_for_segment(policy, segment)["thresholds"]
        segment_records = [record for record in records if str(record.get("project_segment")) == segment]
        calibrated = _calibrate_thresholds_for_segment(current, segment_records, min_samples)
        used_any_history = used_any_history or bool(calibrated["used_history"])
        segment_reports[segment] = {
            "samples": len(segment_records),
            "used_history": calibrated["used_history"],
            "reason": calibrated["reason"],
            "before": current,
            "after": calibrated["thresholds"],
        }
        segment_thresholds[segment] = {"thresholds": calibrated["thresholds"]}

    current_version = str(policy.get("version", "1.1.0"))
    recommended_version = _bump_patch_version(current_version) if used_any_history else current_version
    recommended_policy = _build_recommended_policy(policy, segment_thresholds, recommended_version)

    applied = False
    if apply_updates and used_any_history:
        target = repo_root / POLICY_FILE
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(recommended_policy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        applied = True

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "history_file": history_file,
        "history_records": len(records),
        "min_samples_per_segment": min_samples,
        "policy_version_before": current_version,
        "policy_version_recommended": recommended_version,
        "used_any_history": used_any_history,
        "applied": applied,
        "segments": segment_reports,
        "recommended_policy": recommended_policy,
    }
    return report


def _build_recommended_policy(
    policy: dict[str, Any],
    segment_thresholds: dict[str, Any],
    recommended_version: str,
) -> dict[str, Any]:
    recommended = json.loads(json.dumps(policy))
    recommended["version"] = recommended_version
    recommended["segment_thresholds"] = segment_thresholds
    calibration = recommended.get("calibration", {})
    if not isinstance(calibration, dict):
        calibration = {}
    calibration["last_calibrated_at"] = datetime.now(timezone.utc).isoformat()
    if "min_samples_per_segment" not in calibration:
        calibration["min_samples_per_segment"] = 5
    if "history_file" not in calibration:
        calibration["history_file"] = "docs/audits/proposal_decision_history.jsonl"
    recommended["calibration"] = calibration
    return recommended


def _calibrate_thresholds_for_segment(
    current_thresholds: dict[str, Any],
    records: list[dict[str, Any]],
    min_samples: int,
) -> dict[str, Any]:
    normalized_current = _normalize_thresholds(current_thresholds)
    if len(records) < min_samples:
        return {
            "thresholds": normalized_current,
            "used_history": False,
            "reason": "insufficient_samples",
        }

    scores = sorted(_as_float(record.get("score"), 0.0) for record in records)
    ambiguities = sorted(_as_float(record.get("ambiguity_score"), 0.55) for record in records)
    open_gaps = sorted(max(0, _as_int(record.get("open_gaps"), 0)) for record in records)

    current_go = _as_float(normalized_current["go_min_score"], 0.78)
    current_caveats = _as_float(normalized_current["go_with_caveats_min_score"], 0.52)
    current_no_go = _as_float(normalized_current["no_go_max_score"], 0.40)
    current_go_ambiguity = _as_float(normalized_current["go_max_ambiguity_score"], 0.45)
    current_no_go_ambiguity = _as_float(normalized_current["no_go_min_ambiguity_score"], 0.88)
    current_go_gaps = _as_int(normalized_current["go_max_open_gaps"], 2)
    current_no_go_gaps = _as_int(normalized_current["no_go_min_open_gaps"], 7)

    candidate_go = _clamp(_percentile(scores, 0.70), 0.55, 0.95)
    go_min = _bounded_adjust(current_go, candidate_go, max_delta=0.08, lower=0.55, upper=0.95)

    candidate_caveats = _clamp(_percentile(scores, 0.45), 0.35, go_min - 0.04)
    caveats_min = _bounded_adjust(current_caveats, candidate_caveats, max_delta=0.08, lower=0.35, upper=go_min - 0.04)

    candidate_no_go = _clamp(_percentile(scores, 0.25), 0.20, caveats_min - 0.04)
    no_go_max_score = _bounded_adjust(current_no_go, candidate_no_go, max_delta=0.08, lower=0.20, upper=caveats_min - 0.04)

    candidate_go_ambiguity = _clamp(_percentile(ambiguities, 0.55), 0.25, 0.85)
    go_max_ambiguity = _bounded_adjust(
        current_go_ambiguity,
        candidate_go_ambiguity,
        max_delta=0.15,
        lower=0.25,
        upper=0.85,
    )

    candidate_go_gaps = int(round(_percentile(open_gaps, 0.55)))
    go_max_open_gaps = _bounded_adjust_int(current_go_gaps, candidate_go_gaps, max_delta=2, lower=1, upper=6)

    candidate_no_go_gaps = int(round(_percentile(open_gaps, 0.80)))
    no_go_min_open_gaps = _bounded_adjust_int(
        current_no_go_gaps,
        candidate_no_go_gaps,
        max_delta=2,
        lower=go_max_open_gaps + 1,
        upper=10,
    )
    if no_go_min_open_gaps <= go_max_open_gaps:
        no_go_min_open_gaps = min(10, go_max_open_gaps + 1)

    candidate_no_go_ambiguity = _clamp(_percentile(ambiguities, 0.80), go_max_ambiguity + 0.10, 0.95)
    no_go_min_ambiguity = _bounded_adjust(
        current_no_go_ambiguity,
        candidate_no_go_ambiguity,
        max_delta=0.15,
        lower=max(go_max_ambiguity + 0.05, 0.55),
        upper=0.95,
    )

    calibrated = {
        "go_min_score": round(go_min, 2),
        "go_with_caveats_min_score": round(caveats_min, 2),
        "go_max_ambiguity_score": round(go_max_ambiguity, 2),
        "go_max_open_gaps": int(go_max_open_gaps),
        "no_go_max_score": round(no_go_max_score, 2),
        "no_go_min_open_gaps": int(no_go_min_open_gaps),
        "no_go_min_ambiguity_score": round(no_go_min_ambiguity, 2),
    }
    return {
        "thresholds": calibrated,
        "used_history": True,
        "reason": "calibrated_from_history",
    }


def _load_history_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def _normalize_thresholds(values: dict[str, Any]) -> dict[str, float | int]:
    normalized: dict[str, float | int] = {}
    for key in REQUIRED_THRESHOLD_KEYS:
        raw_value = values.get(key)
        if key.endswith("open_gaps"):
            normalized[key] = _as_int(raw_value, 0)
        else:
            normalized[key] = _as_float(raw_value, 0.0)
    return normalized


def _percentile(values: list[float | int], ratio: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])
    position = _clamp(ratio, 0.0, 1.0) * (len(values) - 1)
    lower = int(position)
    upper = min(len(values) - 1, lower + 1)
    weight = position - lower
    return float(values[lower]) + (float(values[upper]) - float(values[lower])) * weight


def _bump_patch_version(version: str) -> str:
    parts = version.strip().split(".")
    if len(parts) != 3:
        return "1.1.1"
    try:
        major, minor, patch = (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return "1.1.1"
    return f"{major}.{minor}.{patch + 1}"


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _bounded_adjust(current: float, candidate: float, *, max_delta: float, lower: float, upper: float) -> float:
    delta = _clamp(candidate - current, -max_delta, max_delta)
    return _clamp(current + delta, lower, upper)


def _bounded_adjust_int(current: int, candidate: int, *, max_delta: int, lower: int, upper: int) -> int:
    delta = candidate - current
    if delta > max_delta:
        delta = max_delta
    if delta < -max_delta:
        delta = -max_delta
    value = current + delta
    return int(max(lower, min(upper, value)))


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
