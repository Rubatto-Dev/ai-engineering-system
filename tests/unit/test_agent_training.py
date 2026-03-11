from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from ai_engineering_os.agent_training import (
    build_leaderboard_report,
    build_score_history_entry,
    compare_shadow_runs,
)


@pytest.mark.unit
def test_build_score_history_entry_with_full_success() -> None:
    execution = {
        "status": "success",
        "stages": [
            {
                "agent_id": "00",
                "checks": {
                    "decision": "GO",
                    "stage_validation_ok": True,
                    "handoff_packet_ok": True,
                },
            },
            {
                "agent_id": "01",
                "checks": {
                    "stage_validation_ok": True,
                    "handoff_packet_ok": True,
                },
            },
        ],
        "artifacts": [
            "docs/26_proposta_avaliacao.md",
            "docs/28_validacao_pre_kickoff.md",
            "docs/31_politica_decisao_comercial.md",
        ],
    }
    audit = {"status": "audit_ok"}
    weights = {
        "execution_success": 0.30,
        "stage_validation": 0.25,
        "handoff_quality": 0.20,
        "audit_success": 0.15,
        "artifact_coverage": 0.10,
    }

    entry = build_score_history_entry(
        project="alpha",
        cycle=1,
        mode="autopilot_safe",
        profile="primary",
        is_shadow=False,
        execution_result=execution,
        audit_result=audit,
        weights=weights,
    )

    assert entry["decision"] == "GO"
    assert entry["metrics"]["execution_success"] == 1.0
    assert entry["metrics"]["stage_validation"] == 1.0
    assert entry["metrics"]["handoff_quality"] == 1.0
    assert entry["metrics"]["audit_success"] == 1.0
    assert entry["metrics"]["artifact_coverage"] == 1.0
    assert entry["score_global"] == 1.0


@pytest.mark.unit
def test_build_score_history_entry_detects_core_docs_in_absolute_paths() -> None:
    execution = {
        "status": "success",
        "stages": [
            {
                "agent_id": "00",
                "checks": {
                    "decision": "GO",
                    "stage_validation_ok": True,
                    "handoff_packet_ok": True,
                },
            }
        ],
        "artifacts": [
            "C:\\repo\\docs\\26_proposta_avaliacao.md",
            "C:\\repo\\docs\\28_validacao_pre_kickoff.md",
            "C:\\repo\\docs\\31_politica_decisao_comercial.md",
        ],
    }
    audit = {"status": "audit_ok"}
    weights = {
        "execution_success": 0.30,
        "stage_validation": 0.25,
        "handoff_quality": 0.20,
        "audit_success": 0.15,
        "artifact_coverage": 0.10,
    }

    entry = build_score_history_entry(
        project="abs-path-demo",
        cycle=1,
        mode="autopilot_safe",
        profile="primary",
        is_shadow=False,
        execution_result=execution,
        audit_result=audit,
        weights=weights,
    )

    assert entry["metrics"]["artifact_coverage"] == 1.0


@pytest.mark.unit
def test_build_leaderboard_report_ignores_old_records() -> None:
    now = datetime.now(timezone.utc)
    old = now - timedelta(days=120)
    records = [
        {
            "timestamp_utc": old.isoformat(),
            "profile": "primary",
            "decision": "GO",
            "score_global": 0.95,
            "metrics": {"execution_success": 1.0, "audit_success": 1.0, "stage_validation": 1.0, "handoff_quality": 1.0, "artifact_coverage": 1.0},
        },
        {
            "timestamp_utc": now.isoformat(),
            "profile": "primary",
            "decision": "GO_COM_RESSALVAS",
            "score_global": 0.92,
            "metrics": {"execution_success": 1.0, "audit_success": 1.0, "stage_validation": 1.0, "handoff_quality": 1.0, "artifact_coverage": 1.0},
        },
    ]

    report = build_leaderboard_report(
        records=records,
        window_days=30,
        min_runs=1,
        promotion_score=0.90,
        watch_score=0.85,
    )

    assert report["records_total"] == 2
    assert report["records_in_window"] == 1
    assert report["profiles"][0]["runs"] == 1


@pytest.mark.unit
def test_build_leaderboard_report_marks_promote_for_stable_top_profile() -> None:
    now = datetime.now(timezone.utc)
    records = []
    for _ in range(3):
        records.append(
            {
                "timestamp_utc": now.isoformat(),
                "profile": "primary",
                "decision": "GO",
                "score_global": 0.94,
                "metrics": {
                    "execution_success": 1.0,
                    "audit_success": 1.0,
                    "stage_validation": 1.0,
                    "handoff_quality": 1.0,
                    "artifact_coverage": 0.9,
                },
            }
        )
    records.append(
        {
            "timestamp_utc": now.isoformat(),
            "profile": "shadow_autopilot_full",
            "decision": "GO_COM_RESSALVAS",
            "score_global": 0.86,
            "metrics": {
                "execution_success": 1.0,
                "audit_success": 1.0,
                "stage_validation": 0.9,
                "handoff_quality": 0.9,
                "artifact_coverage": 0.9,
            },
        }
    )

    report = build_leaderboard_report(
        records=records,
        window_days=30,
        min_runs=3,
        promotion_score=0.90,
        watch_score=0.85,
    )

    assert report["top_profile"] == "primary"
    assert report["profiles"][0]["recommended_action"] == "promote"


@pytest.mark.unit
def test_compare_shadow_runs_detects_winner_and_decision_change() -> None:
    primary = {
        "profile": "primary",
        "mode": "autopilot_safe",
        "decision": "GO",
        "score_global": 0.91,
        "metrics": {},
    }
    shadow = {
        "profile": "shadow_autopilot_full",
        "mode": "autopilot_full",
        "decision": "GO_COM_RESSALVAS",
        "score_global": 0.95,
        "metrics": {},
    }

    report = compare_shadow_runs(primary, shadow)

    assert report["winner"] == "shadow"
    assert report["decision_changed"] is True
    assert report["score_delta"] == 0.04
