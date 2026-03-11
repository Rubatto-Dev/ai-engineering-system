from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering_os.quality_gate import evaluate_quality_gate
from ai_engineering_os.repository import ensure_structure


@pytest.mark.unit
def test_quality_gate_passes_with_default_structure(tmp_path: Path) -> None:
    ensure_structure(tmp_path)
    gate = evaluate_quality_gate(tmp_path)
    assert gate["ok"] is True
    assert gate["checks"]["mcp_servers_configured"] is True
    assert gate["checks"]["sonarqube_configured"] is True


@pytest.mark.unit
def test_quality_gate_fails_when_mcp_servers_are_invalid(tmp_path: Path) -> None:
    ensure_structure(tmp_path)
    (tmp_path / "config" / "mcp-servers.json").write_text('{"mcpServers": {}}', encoding="utf-8")

    gate = evaluate_quality_gate(tmp_path)
    assert gate["ok"] is False
    assert gate["checks"]["mcp_servers_configured"] is False


@pytest.mark.unit
def test_quality_gate_fails_when_sonar_properties_are_incomplete(tmp_path: Path) -> None:
    ensure_structure(tmp_path)
    (tmp_path / "sonar-project.properties").write_text("sonar.projectKey=test\n", encoding="utf-8")

    gate = evaluate_quality_gate(tmp_path)
    assert gate["ok"] is False
    assert gate["checks"]["sonarqube_configured"] is False
    assert gate["checks"]["quality_gate_ok"] is False
