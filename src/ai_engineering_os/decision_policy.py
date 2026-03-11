from __future__ import annotations

import json
from pathlib import Path
from typing import Any


POLICY_FILE = Path("config") / "decision_policy.json"
PROJECT_SEGMENTS = ["frontend", "backend", "automacao", "fullstack"]
REQUIRED_THRESHOLD_KEYS = [
    "go_min_score",
    "go_with_caveats_min_score",
    "go_max_ambiguity_score",
    "go_max_open_gaps",
    "no_go_max_score",
    "no_go_min_open_gaps",
    "no_go_min_ambiguity_score",
]

_DEFAULT_THRESHOLDS: dict[str, float | int] = {
    "go_min_score": 0.78,
    "go_with_caveats_min_score": 0.52,
    "go_max_ambiguity_score": 0.45,
    "go_max_open_gaps": 2,
    "no_go_max_score": 0.40,
    "no_go_min_open_gaps": 7,
    "no_go_min_ambiguity_score": 0.88,
}

_DEFAULT_POLICY: dict[str, Any] = {
    "version": "1.1.0",
    "thresholds": _DEFAULT_THRESHOLDS,
    "labels": {
        "go": "GO",
        "go_with_caveats": "GO_COM_RESSALVAS",
        "no_go": "NO_GO",
    },
    "segment_thresholds": {
        "frontend": {
            "thresholds": {
                "go_min_score": 0.76,
                "go_with_caveats_min_score": 0.50,
                "go_max_ambiguity_score": 0.42,
                "go_max_open_gaps": 2,
                "no_go_max_score": 0.38,
                "no_go_min_open_gaps": 6,
                "no_go_min_ambiguity_score": 0.85,
            }
        },
        "backend": {
            "thresholds": {
                "go_min_score": 0.80,
                "go_with_caveats_min_score": 0.54,
                "go_max_ambiguity_score": 0.40,
                "go_max_open_gaps": 2,
                "no_go_max_score": 0.40,
                "no_go_min_open_gaps": 6,
                "no_go_min_ambiguity_score": 0.84,
            }
        },
        "automacao": {
            "thresholds": {
                "go_min_score": 0.74,
                "go_with_caveats_min_score": 0.50,
                "go_max_ambiguity_score": 0.48,
                "go_max_open_gaps": 3,
                "no_go_max_score": 0.36,
                "no_go_min_open_gaps": 7,
                "no_go_min_ambiguity_score": 0.86,
            }
        },
        "fullstack": {
            "thresholds": {
                "go_min_score": 0.79,
                "go_with_caveats_min_score": 0.53,
                "go_max_ambiguity_score": 0.44,
                "go_max_open_gaps": 2,
                "no_go_max_score": 0.39,
                "no_go_min_open_gaps": 7,
                "no_go_min_ambiguity_score": 0.87,
            }
        },
    },
    "calibration": {
        "min_samples_per_segment": 5,
        "history_file": "docs/audits/proposal_decision_history.jsonl",
        "last_calibrated_at": None,
    },
}


def load_decision_policy(repo_root: Path) -> dict[str, Any]:
    policy = _deep_copy(_DEFAULT_POLICY)
    policy["source"] = "default"
    candidate = repo_root / POLICY_FILE
    if not candidate.exists():
        return policy

    try:
        payload = json.loads(candidate.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        policy["source"] = "default_fallback"
        policy["load_error"] = "decision_policy_json_invalid"
        return policy

    if not isinstance(payload, dict):
        policy["source"] = "default_fallback"
        policy["load_error"] = "decision_policy_invalid_shape"
        return policy

    merged = _merge_policy(policy, payload)
    merged["source"] = "config"
    return merged


def resolve_thresholds_for_segment(policy: dict[str, Any], project_segment: str) -> dict[str, Any]:
    segment = project_segment if project_segment in PROJECT_SEGMENTS else "fullstack"
    base = _normalize_thresholds(policy.get("thresholds", {}), _DEFAULT_THRESHOLDS)

    segment_thresholds = (
        policy.get("segment_thresholds", {}).get(segment, {}).get("thresholds", {})
        if isinstance(policy.get("segment_thresholds"), dict)
        else {}
    )
    merged = _normalize_thresholds(segment_thresholds, base)
    return {"project_segment": segment, "thresholds": merged}


def classify_commercial_decision(
    score: float,
    proposal_profile: dict[str, Any] | None,
    policy: dict[str, Any] | None,
) -> dict[str, Any]:
    profile = proposal_profile if isinstance(proposal_profile, dict) else {}
    active_policy = _merge_policy(_deep_copy(_DEFAULT_POLICY), policy if isinstance(policy, dict) else {})
    labels = active_policy["labels"]
    segment = _segment_from_profile(profile)
    resolved = resolve_thresholds_for_segment(active_policy, segment)
    thresholds = resolved["thresholds"]

    go_min = float(thresholds["go_min_score"])
    caveats_min = float(thresholds["go_with_caveats_min_score"])
    go_max_ambiguity = float(thresholds["go_max_ambiguity_score"])
    go_max_open_gaps = int(thresholds["go_max_open_gaps"])
    no_go_max_score = float(thresholds["no_go_max_score"])
    no_go_min_open_gaps = int(thresholds["no_go_min_open_gaps"])
    no_go_min_ambiguity = float(thresholds["no_go_min_ambiguity_score"])

    missing_info = profile.get("missing_information", [])
    open_gaps = len(missing_info) if isinstance(missing_info, list) else 0
    ambiguity_score = _as_float(profile.get("ambiguity_score"), 0.55)
    feasibility = str(profile.get("feasibility", "media")).lower()

    base_decision = labels["no_go"]
    if score >= go_min:
        base_decision = labels["go"]
    elif score >= caveats_min:
        base_decision = labels["go_with_caveats"]

    decision = base_decision
    reasons: list[str] = []

    if decision == labels["go"]:
        if feasibility == "baixa":
            decision = labels["go_with_caveats"]
            reasons.append("feasibility_baixa_limits_go")
        if ambiguity_score > go_max_ambiguity:
            decision = labels["go_with_caveats"]
            reasons.append("ambiguity_above_go_threshold")
        if open_gaps > go_max_open_gaps:
            decision = labels["go_with_caveats"]
            reasons.append("open_gaps_above_go_threshold")

    if score <= no_go_max_score and (feasibility == "baixa" or ambiguity_score >= no_go_min_ambiguity):
        decision = labels["no_go"]
        reasons.append("score_too_low_for_current_risk")
    if open_gaps >= no_go_min_open_gaps and ambiguity_score >= no_go_min_ambiguity:
        decision = labels["no_go"]
        reasons.append("critical_discovery_gaps_and_high_ambiguity")
    if decision == labels["go_with_caveats"] and score < caveats_min:
        decision = labels["no_go"]
        reasons.append("score_below_caveats_threshold")

    if not reasons:
        reasons.append("base_score_threshold_applied")

    scope_lock_ready = (
        decision == labels["go"]
        and feasibility != "baixa"
        and ambiguity_score <= go_max_ambiguity
        and open_gaps <= go_max_open_gaps
    )

    return {
        "decision": decision,
        "base_decision": base_decision,
        "policy_version": str(active_policy.get("version", "unknown")),
        "project_segment": segment,
        "thresholds": thresholds,
        "reasons": reasons,
        "context": {
            "score": round(score, 4),
            "feasibility": feasibility,
            "ambiguity_score": ambiguity_score,
            "open_gaps": open_gaps,
        },
        "scope_lock_ready": scope_lock_ready,
    }


def _merge_policy(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = _deep_copy(base)

    if "version" in override and isinstance(override["version"], str) and override["version"].strip():
        merged["version"] = override["version"].strip()

    merged["thresholds"] = _normalize_thresholds(override.get("thresholds", {}), merged["thresholds"])

    labels = merged.get("labels", {})
    if isinstance(override.get("labels"), dict):
        for key, default_value in labels.items():
            value = override["labels"].get(key)
            labels[key] = value.strip() if isinstance(value, str) and value.strip() else default_value
    merged["labels"] = labels

    segment_thresholds = merged.get("segment_thresholds", {})
    override_segments = override.get("segment_thresholds")
    if isinstance(override_segments, dict):
        for segment in PROJECT_SEGMENTS:
            baseline = segment_thresholds.get(segment, {}).get("thresholds", merged["thresholds"])
            raw_segment = override_segments.get(segment, {})
            if isinstance(raw_segment, dict):
                if isinstance(raw_segment.get("thresholds"), dict):
                    candidate = raw_segment["thresholds"]
                else:
                    candidate = raw_segment
                normalized = _normalize_thresholds(candidate, baseline)
                segment_thresholds[segment] = {"thresholds": normalized}
    merged["segment_thresholds"] = segment_thresholds

    calibration = merged.get("calibration", {})
    override_calibration = override.get("calibration")
    if isinstance(override_calibration, dict):
        calibration["min_samples_per_segment"] = _as_int(
            override_calibration.get("min_samples_per_segment"),
            _as_int(calibration.get("min_samples_per_segment"), 5),
        )
        history_file = override_calibration.get("history_file")
        if isinstance(history_file, str) and history_file.strip():
            calibration["history_file"] = history_file.strip()
        last_calibrated_at = override_calibration.get("last_calibrated_at")
        if isinstance(last_calibrated_at, str) and last_calibrated_at.strip():
            calibration["last_calibrated_at"] = last_calibrated_at.strip()
    merged["calibration"] = calibration

    return merged


def _normalize_thresholds(raw: Any, fallback: dict[str, float | int]) -> dict[str, float | int]:
    normalized = _deep_copy(fallback)
    if not isinstance(raw, dict):
        return normalized

    for key, default_value in fallback.items():
        value = raw.get(key)
        if isinstance(default_value, int):
            normalized[key] = _as_int(value, int(default_value))
        else:
            normalized[key] = _as_float(value, float(default_value))
    return normalized


def _segment_from_profile(profile: dict[str, Any]) -> str:
    project_type = str(profile.get("project_type", "fullstack")).strip().lower()
    if project_type in PROJECT_SEGMENTS:
        return project_type
    return "fullstack"


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


def _deep_copy(value: Any) -> Any:
    return json.loads(json.dumps(value))
