from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from ai_engineering_os.decision_calibration import calibrate_decision_policy
from ai_engineering_os.repository import ensure_structure


@pytest.mark.unit
def test_calibration_keeps_thresholds_when_samples_are_insufficient(tmp_path: Path) -> None:
    ensure_structure(tmp_path)
    history_path = tmp_path / "docs" / "audits" / "proposal_decision_history.jsonl"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(
        json.dumps(
            {
                "project": "alpha",
                "project_segment": "fullstack",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "score": 0.72,
                "ambiguity_score": 0.40,
                "open_gaps": 2,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    report = calibrate_decision_policy(tmp_path, apply_updates=False)

    assert report["history_records"] == 1
    assert report["segments"]["fullstack"]["used_history"] is False
    assert report["segments"]["fullstack"]["reason"] == "insufficient_samples"


@pytest.mark.unit
def test_calibration_updates_policy_when_history_has_enough_samples(tmp_path: Path) -> None:
    ensure_structure(tmp_path)
    policy_path = tmp_path / "config" / "decision_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["calibration"]["min_samples_per_segment"] = 2
    policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")

    history_path = tmp_path / "docs" / "audits" / "proposal_decision_history.jsonl"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for segment in ("frontend", "backend", "automacao", "fullstack"):
        records.append(
            {
                "project": f"{segment}-a",
                "project_segment": segment,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "score": 0.82,
                "ambiguity_score": 0.32,
                "open_gaps": 1,
            }
        )
        records.append(
            {
                "project": f"{segment}-b",
                "project_segment": segment,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "score": 0.64,
                "ambiguity_score": 0.58,
                "open_gaps": 4,
            }
        )
    history_path.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")

    report = calibrate_decision_policy(tmp_path, apply_updates=True)

    assert report["applied"] is True
    assert report["segments"]["frontend"]["used_history"] is True
    updated_policy = json.loads(policy_path.read_text(encoding="utf-8"))
    assert updated_policy["version"] != policy["version"]
    assert updated_policy["calibration"]["last_calibrated_at"] is not None
    assert (
        updated_policy["segment_thresholds"]["frontend"]["thresholds"]["go_with_caveats_min_score"]
        != policy["segment_thresholds"]["frontend"]["thresholds"]["go_with_caveats_min_score"]
    )


@pytest.mark.unit
def test_calibration_ignores_records_outside_window(tmp_path: Path) -> None:
    ensure_structure(tmp_path)
    policy_path = tmp_path / "config" / "decision_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["calibration"]["window_days"] = 30
    policy["calibration"]["min_samples_per_segment"] = 2
    policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")

    old_timestamp = (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()
    history_path = tmp_path / "docs" / "audits" / "proposal_decision_history.jsonl"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "project": "frontend-old-a",
                        "project_segment": "frontend",
                        "timestamp_utc": old_timestamp,
                        "score": 0.80,
                        "ambiguity_score": 0.40,
                        "open_gaps": 2,
                    }
                ),
                json.dumps(
                    {
                        "project": "frontend-old-b",
                        "project_segment": "frontend",
                        "timestamp_utc": old_timestamp,
                        "score": 0.70,
                        "ambiguity_score": 0.45,
                        "open_gaps": 3,
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = calibrate_decision_policy(tmp_path, apply_updates=True)

    assert report["history_records"] == 2
    assert report["history_records_in_window"] == 0
    assert report["segments"]["frontend"]["used_history"] is False
    assert report["segments"]["frontend"]["reason"] == "insufficient_samples"
    assert report["applied"] is False


@pytest.mark.unit
def test_calibration_requires_minimum_variance(tmp_path: Path) -> None:
    ensure_structure(tmp_path)
    policy_path = tmp_path / "config" / "decision_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["calibration"]["min_samples_per_segment"] = 3
    policy["calibration"]["min_score_spread"] = 0.15
    policy["calibration"]["min_ambiguity_spread"] = 0.15
    policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")

    now_ts = datetime.now(timezone.utc).isoformat()
    history_path = tmp_path / "docs" / "audits" / "proposal_decision_history.jsonl"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    records = [
        {
            "project": "backend-a",
            "project_segment": "backend",
            "timestamp_utc": now_ts,
            "score": 0.74,
            "ambiguity_score": 0.50,
            "open_gaps": 2,
        },
        {
            "project": "backend-b",
            "project_segment": "backend",
            "timestamp_utc": now_ts,
            "score": 0.75,
            "ambiguity_score": 0.51,
            "open_gaps": 2,
        },
        {
            "project": "backend-c",
            "project_segment": "backend",
            "timestamp_utc": now_ts,
            "score": 0.76,
            "ambiguity_score": 0.52,
            "open_gaps": 3,
        },
    ]
    history_path.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")

    report = calibrate_decision_policy(tmp_path, apply_updates=False)

    assert report["segments"]["backend"]["used_history"] is False
    assert report["segments"]["backend"]["reason"] == "insufficient_variance"
