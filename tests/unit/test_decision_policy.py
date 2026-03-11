from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_engineering_os.decision_policy import classify_commercial_decision, load_decision_policy


@pytest.mark.unit
def test_decision_policy_returns_go_for_high_score_low_risk(tmp_path: Path) -> None:
    policy = load_decision_policy(tmp_path)
    profile = {
        "feasibility": "alta",
        "ambiguity_score": 0.30,
        "missing_information": ["deadline"],
    }

    result = classify_commercial_decision(0.84, profile, policy)

    assert result["decision"] == "GO"
    assert result["scope_lock_ready"] is True


@pytest.mark.unit
def test_decision_policy_downgrades_go_when_ambiguity_is_high(tmp_path: Path) -> None:
    policy = load_decision_policy(tmp_path)
    profile = {
        "feasibility": "media",
        "ambiguity_score": 0.79,
        "missing_information": ["target_users", "budget", "deadline"],
    }

    result = classify_commercial_decision(0.86, profile, policy)

    assert result["base_decision"] == "GO"
    assert result["decision"] == "GO_COM_RESSALVAS"
    assert "ambiguity_above_go_threshold" in result["reasons"]


@pytest.mark.unit
def test_load_decision_policy_reads_versioned_config(tmp_path: Path) -> None:
    config = tmp_path / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "decision_policy.json").write_text(
        json.dumps(
            {
                "version": "1.2.0",
                "thresholds": {
                    "go_min_score": 0.80,
                    "go_with_caveats_min_score": 0.60,
                    "go_max_ambiguity_score": 0.40,
                    "go_max_open_gaps": 1,
                    "no_go_max_score": 0.30,
                    "no_go_min_open_gaps": 8,
                    "no_go_min_ambiguity_score": 0.92,
                },
                "labels": {
                    "go": "GO",
                    "go_with_caveats": "GO_COM_RESSALVAS",
                    "no_go": "NO_GO",
                },
                "segment_thresholds": {
                    "frontend": {"thresholds": {"go_min_score": 0.81}},
                    "backend": {"thresholds": {"go_min_score": 0.82}},
                    "automacao": {"thresholds": {"go_min_score": 0.73}},
                    "fullstack": {"thresholds": {"go_min_score": 0.80}},
                },
                "calibration": {
                    "min_samples_per_segment": 3,
                    "history_file": "docs/audits/proposal_decision_history.jsonl",
                },
            }
        ),
        encoding="utf-8",
    )

    policy = load_decision_policy(tmp_path)

    assert policy["version"] == "1.2.0"
    assert policy["source"] == "config"
    assert policy["thresholds"]["go_min_score"] == 0.80
    assert policy["segment_thresholds"]["backend"]["thresholds"]["go_min_score"] == 0.82


@pytest.mark.unit
def test_decision_policy_uses_segment_thresholds_when_project_type_is_backend(tmp_path: Path) -> None:
    policy = load_decision_policy(tmp_path)
    profile = {
        "project_type": "backend",
        "feasibility": "alta",
        "ambiguity_score": 0.35,
        "missing_information": ["deadline"],
    }

    result = classify_commercial_decision(0.79, profile, policy)

    assert result["project_segment"] == "backend"
    assert result["thresholds"]["go_min_score"] == 0.80
    assert result["decision"] == "GO_COM_RESSALVAS"
