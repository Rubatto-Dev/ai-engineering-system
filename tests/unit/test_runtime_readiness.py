from __future__ import annotations

from pathlib import Path

import pytest

import ai_engineering_os.external_runtime as runtime_module


def _ok_command_probe(command: list[str], _cwd: Path, timeout: float) -> dict[str, object]:
    _ = timeout
    return {
        "ok": True,
        "command": command,
        "mode": "exited",
        "exit_code": 0,
        "stdout": "",
        "stderr": "",
    }


@pytest.mark.unit
def test_runtime_readiness_fails_when_sonar_is_unreachable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runtime_module, "_probe_command", _ok_command_probe)
    monkeypatch.setattr(runtime_module, "_probe_mcp_server", lambda *_args, **_kwargs: {"ok": True})
    monkeypatch.setattr(runtime_module, "_read_mcp_config", lambda _path: {"mcpServers": {"context7": {}, "sequential-thinking": {}}})
    monkeypatch.setattr(
        runtime_module,
        "_probe_sonar_api",
        lambda: {"ok": False, "url": "http://localhost:9000/api/system/status", "error": "connection_refused"},
    )

    result = runtime_module.evaluate_runtime_readiness(tmp_path)

    assert result["ok"] is False
    assert result["checks"]["node_available"] is True
    assert result["checks"]["npm_available"] is True
    assert result["checks"]["context7_runtime_ready"] is True
    assert result["checks"]["sequential_thinking_runtime_ready"] is True
    assert result["checks"]["sonar_api_reachable"] is False
    assert result["details"]["sonarqube"]["error"] == "connection_refused"


@pytest.mark.unit
def test_runtime_readiness_passes_when_all_probes_are_ready(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runtime_module, "_probe_command", _ok_command_probe)
    monkeypatch.setattr(runtime_module, "_probe_mcp_server", lambda *_args, **_kwargs: {"ok": True})
    monkeypatch.setattr(runtime_module, "_read_mcp_config", lambda _path: {"mcpServers": {"context7": {}, "sequential-thinking": {}}})
    monkeypatch.setattr(
        runtime_module,
        "_probe_sonar_api",
        lambda: {"ok": True, "status_code": 200, "system_status": "UP"},
    )

    result = runtime_module.evaluate_runtime_readiness(tmp_path)

    assert result["ok"] is True
    assert all(result["checks"].values())
