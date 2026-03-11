from __future__ import annotations

import json
from pathlib import Path
from typing import Any


POLICY_FILE = Path("config") / "decision_policy.json"

_DEFAULT_POLICY: dict[str, Any] = {
    "version": "1.0.0",
    "thresholds": {
        "go_min_score": 0.78,
        "go_with_caveats_min_score": 0.52,
        "go_max_ambiguity_score": 0.45,
        "go_max_open_gaps": 2,
        "no_go_max_score": 0.40,
        "no_go_min_open_gaps": 7,
        "no_go_min_ambiguity_score": 0.88,
    },
    "labels": {
        "go": "GO",
        "go_with_caveats": "GO_COM_RESSALVAS",
        "no_go": "NO_GO",
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


def classify_commercial_decision(
    score: float,
    proposal_profile: dict[str, Any] | None,
    policy: dict[str, Any] | None,
) -> dict[str, Any]:
    profile = proposal_profile if isinstance(proposal_profile, dict) else {}
    active_policy = _merge_policy(_deep_copy(_DEFAULT_POLICY), policy if isinstance(policy, dict) else {})
    thresholds = active_policy["thresholds"]
    labels = active_policy["labels"]

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

    thresholds = merged.get("thresholds", {})
    if isinstance(override.get("thresholds"), dict):
        for key, default_value in thresholds.items():
            if isinstance(default_value, int):
                thresholds[key] = _as_int(override["thresholds"].get(key), default_value)
            else:
                thresholds[key] = _as_float(override["thresholds"].get(key), float(default_value))
    merged["thresholds"] = thresholds

    labels = merged.get("labels", {})
    if isinstance(override.get("labels"), dict):
        for key, default_value in labels.items():
            value = override["labels"].get(key)
            if isinstance(value, str) and value.strip():
                labels[key] = value.strip()
            else:
                labels[key] = default_value
    merged["labels"] = labels
    return merged


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


def _deep_copy(value: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(value))
