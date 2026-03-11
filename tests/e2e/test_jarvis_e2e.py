from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering_os.jarvis import JarvisEngine


@pytest.mark.e2e
def test_full_jarvis_cycle_and_ship(tmp_path: Path) -> None:
    engine = JarvisEngine(tmp_path)

    start = engine.handle("JARVIS: START project=alpha")
    assert start["status"] == "started"

    plan = engine.handle("JARVIS: PLAN cycle=1")
    assert plan["status"] == "planned"
    assert len(plan["steps"]) >= 15
    assert plan["agents_expected"] == 15

    exec_result = engine.handle("JARVIS: EXEC cycle=1 mode=autopilot_safe")
    assert exec_result["status"] == "success"
    assert exec_result["agent_count"] == 15

    audit = engine.handle("JARVIS: AUDIT repo=alpha tests_ok=true security_ok=true sonar_ok=true")
    assert audit["status"] == "audit_ok"
    assert audit["result"]["checks"]["context7_configured"] is True
    assert audit["result"]["checks"]["mcp_servers_configured"] is True
    assert audit["result"]["checks"]["sonarqube_configured"] is True

    ship = engine.handle("JARVIS: SHIP version=0.1.0")
    assert ship["status"] == "shipped"
    notes = tmp_path / "docs" / "16_release_notes.md"
    assert notes.exists()
    assert "Release 0.1.0" in notes.read_text(encoding="utf-8")


@pytest.mark.e2e
def test_ship_requires_audit_for_latest_execution(tmp_path: Path) -> None:
    engine = JarvisEngine(tmp_path)
    engine.handle("JARVIS: START project=alpha")
    engine.handle("JARVIS: EXEC cycle=1 mode=autopilot_safe")

    blocked = engine.handle("JARVIS: SHIP version=0.1.0")
    assert blocked["status"] == "ship_blocked"
    assert blocked["reason"] == "audit_required"


@pytest.mark.e2e
def test_audit_uses_execution_defaults_when_flags_are_omitted(tmp_path: Path) -> None:
    engine = JarvisEngine(tmp_path)
    engine.handle("JARVIS: START project=alpha")
    engine.handle("JARVIS: EXEC cycle=1 mode=autopilot_safe")

    audit = engine.handle("JARVIS: AUDIT repo=alpha")
    assert audit["status"] == "audit_ok"
    assert audit["inputs"]["tests_ok"] is True
    assert audit["inputs"]["security_ok"] is True
    assert audit["inputs"]["sonar_ok"] is None
