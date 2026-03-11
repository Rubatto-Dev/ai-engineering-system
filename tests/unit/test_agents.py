from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering_os.agents import BacklogAgent, IdeaValidatorAgent, ScopeDefinitionAgent, build_agent_team
from ai_engineering_os.models import AgentResult


@pytest.mark.unit
def test_idea_validator_returns_go_for_good_metrics() -> None:
    result = IdeaValidatorAgent().evaluate(
        {
            "clarity": 0.95,
            "complexity": 0.2,
            "dependency_risk": 0.2,
            "operational_risk": 0.2,
            "time_confidence": 0.9,
            "cost_confidence": 0.8,
        }
    )
    assert result["decision"] == "GO"


@pytest.mark.unit
def test_backlog_agent_generates_items_with_acceptance_criteria() -> None:
    items = BacklogAgent().generate("alpha")
    assert len(items) >= 3
    assert all(item.acceptance_criteria for item in items)


@pytest.mark.unit
def test_build_agent_team_contains_all_agent_ids(tmp_path: Path) -> None:
    team = build_agent_team(tmp_path)
    unique_ids = {agent.agent_id for agent in team}

    assert unique_ids == {"00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14"}
    assert len(team) == 16
    assert team[0].agent_id == "00"
    assert team[-1].agent_id == "08"


@pytest.mark.unit
def test_contract_enforcement_fails_on_handoff_mismatch(tmp_path: Path) -> None:
    agent = ScopeDefinitionAgent(repo_root=tmp_path)
    result = AgentResult(
        agent_id="03",
        agent_name="Scope Definition",
        stage="Scope Definition",
        status="success",
        handoff="99",
    )

    enforced = agent.enforce_contract(result)

    assert enforced.status == "failed"
    assert enforced.checks["contract_loaded"] is True
    assert enforced.checks["contract_handoff_match"] is False


@pytest.mark.unit
def test_contract_enforcement_fails_when_required_section_is_missing(tmp_path: Path) -> None:
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "03_scope.agent.md").write_text(
        "\n".join(
            [
                "# Agent 03 - Scope",
                "",
                "## Role",
                "Define scope.",
                "",
                "## Inputs",
                "- requirements",
                "",
                "## Processing",
                "- consolidate scope",
                "",
                "## Outputs",
                "- docs/01_visao.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    agent = ScopeDefinitionAgent(repo_root=tmp_path)
    result = AgentResult(
        agent_id="03",
        agent_name="Scope Definition",
        stage="Scope Definition",
        status="success",
        handoff="10",
    )
    enforced = agent.enforce_contract(result)

    assert enforced.status == "failed"
    assert enforced.checks["contract_required_sections_ok"] is False
    assert "Handoff" in enforced.checks["contract_missing_sections"]
