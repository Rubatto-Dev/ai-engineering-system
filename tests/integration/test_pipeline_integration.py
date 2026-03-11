from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering_os.pipeline import EngineeringPipeline


@pytest.mark.integration
def test_pipeline_creates_required_artifacts(tmp_path: Path) -> None:
    pipeline = EngineeringPipeline(tmp_path)
    result = pipeline.run(project="alpha", cycle=1, mode="autopilot_safe")

    assert result["status"] == "success"
    assert (tmp_path / "docs" / "10_backlog.md").exists()
    assert (tmp_path / "memory" / "projects" / "alpha.md").exists()
    assert (tmp_path / "memory" / "lessons" / "alpha_lessons.md").exists()


@pytest.mark.integration
def test_pipeline_executes_all_agents_with_traceability(tmp_path: Path) -> None:
    pipeline = EngineeringPipeline(tmp_path)
    result = pipeline.run(project="beta", cycle=2, mode="autopilot_safe")

    assert result["status"] == "success"
    assert result["agent_count"] == 15

    traces = result["stages"]
    assert len(traces) == 16

    executed_ids = {trace["agent_id"] for trace in traces}
    assert executed_ids == {"00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14"}

    assert traces[0]["agent_id"] == "00"
    assert traces[-1]["agent_id"] == "08"
    assert all("handoff" in trace for trace in traces)
    assert all("contract_loaded" in trace["checks"] for trace in traces)
    assert all(trace["checks"].get("contract_handoff_match") is True for trace in traces)
