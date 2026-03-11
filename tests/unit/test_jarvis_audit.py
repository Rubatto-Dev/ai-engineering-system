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
