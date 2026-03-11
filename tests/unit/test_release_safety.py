from __future__ import annotations

from pathlib import Path

import pytest

import ai_engineering_os.release_safety as release_safety


@pytest.mark.unit
def test_release_safety_reports_ok_when_all_checks_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(release_safety, "_run_pytest", lambda _repo: {"ok": True})
    monkeypatch.setattr(release_safety, "evaluate_quality_gate", lambda _repo, tests_ok: {"ok": tests_ok})
    monkeypatch.setattr(release_safety, "evaluate_runtime_readiness", lambda _repo: {"ok": True, "checks": {"sonar_api_reachable": True}})

    class _JarvisOk:
        def __init__(self, _repo_root: Path) -> None:
            pass

        def handle(self, _command: str) -> dict[str, object]:
            return {"status": "audit_ok"}

    monkeypatch.setattr(release_safety, "JarvisEngine", _JarvisOk)

    report = release_safety.run_release_safety_audit(tmp_path)

    assert report["ok"] is True
    assert report["checks"]["tests_ok"] is True
    assert report["checks"]["quality_ok"] is True
    assert report["checks"]["runtime_ok"] is True
    assert report["checks"]["strict_audit_ok"] is True


@pytest.mark.unit
def test_release_safety_reports_fail_when_strict_audit_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(release_safety, "_run_pytest", lambda _repo: {"ok": True})
    monkeypatch.setattr(release_safety, "evaluate_quality_gate", lambda _repo, tests_ok: {"ok": tests_ok})
    monkeypatch.setattr(release_safety, "evaluate_runtime_readiness", lambda _repo: {"ok": True, "checks": {"sonar_api_reachable": True}})

    class _JarvisFail:
        def __init__(self, _repo_root: Path) -> None:
            pass

        def handle(self, _command: str) -> dict[str, object]:
            return {"status": "audit_failed"}

    monkeypatch.setattr(release_safety, "JarvisEngine", _JarvisFail)

    report = release_safety.run_release_safety_audit(tmp_path)

    assert report["ok"] is False
    assert report["checks"]["tests_ok"] is True
    assert report["checks"]["strict_audit_ok"] is False
