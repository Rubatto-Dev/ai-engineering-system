from __future__ import annotations

from pathlib import Path

import pytest

import ai_engineering_os.jarvis as jarvis_module
from ai_engineering_os.jarvis import JarvisEngine


@pytest.mark.unit
def test_audit_strict_external_blocks_when_runtime_is_not_ready(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = JarvisEngine(tmp_path)
    engine.handle("JARVIS: START project=alpha")
    engine.handle("JARVIS: EXEC cycle=1 mode=autopilot_safe")

    monkeypatch.setattr(
        jarvis_module,
        "evaluate_runtime_readiness",
        lambda _repo_root: {"ok": False, "checks": {"sonar_api_reachable": False}, "details": {}},
    )

    audit = engine.handle("JARVIS: AUDIT repo=alpha strict_external=true")

    assert audit["status"] == "audit_failed"
    assert audit["inputs"]["strict_external"] is True
    assert audit["result"]["checks"]["external_runtime_ok"] is False


@pytest.mark.unit
def test_audit_strict_external_passes_when_runtime_is_ready(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = JarvisEngine(tmp_path)
    engine.handle("JARVIS: START project=alpha")
    engine.handle("JARVIS: EXEC cycle=1 mode=autopilot_safe")

    monkeypatch.setattr(
        jarvis_module,
        "evaluate_runtime_readiness",
        lambda _repo_root: {"ok": True, "checks": {"sonar_api_reachable": True}, "details": {}},
    )

    audit = engine.handle("JARVIS: AUDIT repo=alpha strict_external=true")

    assert audit["status"] == "audit_ok"
    assert audit["inputs"]["strict_external"] is True
    assert audit["result"]["checks"]["external_runtime_ok"] is True


@pytest.mark.unit
def test_ship_is_blocked_after_strict_external_audit_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = JarvisEngine(tmp_path)
    engine.handle("JARVIS: START project=alpha")
    engine.handle("JARVIS: EXEC cycle=1 mode=autopilot_safe")

    monkeypatch.setattr(
        jarvis_module,
        "evaluate_runtime_readiness",
        lambda _repo_root: {"ok": False, "checks": {"sonar_api_reachable": False}, "details": {}},
    )

    audit = engine.handle("JARVIS: AUDIT repo=alpha strict_external=true")
    ship = engine.handle("JARVIS: SHIP version=0.1.0")

    assert audit["status"] == "audit_failed"
    assert ship["status"] == "ship_blocked"
    assert ship["reason"] == "audit_failed"
