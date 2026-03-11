from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering_os.agents.scope import ScopeDefinitionAgent
from ai_engineering_os.models import AgentResult, ProjectContext
from ai_engineering_os.pipeline import EngineeringPipeline
from ai_engineering_os.proposal_profile import build_proposal_profile


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
    assert all(trace["checks"].get("result_schema_ok") is True for trace in traces)
    assert all("contract_loaded" in trace["checks"] for trace in traces)
    assert all(trace["checks"].get("contract_handoff_match") is True for trace in traces)


@pytest.mark.integration
def test_pipeline_stops_when_handoff_contract_is_violated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def _broken_scope_run(
        self: ScopeDefinitionAgent,
        _context: ProjectContext,
        _state: dict[str, object],
    ) -> AgentResult:
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[],
            notes="forced invalid handoff for failure-mode coverage",
            checks={},
            outputs={"scope": {"forced": True}},
            handoff="99",
        )

    monkeypatch.setattr(ScopeDefinitionAgent, "run", _broken_scope_run)

    pipeline = EngineeringPipeline(tmp_path)
    result = pipeline.run(project="gamma", cycle=3, mode="autopilot_safe")

    assert result["status"] == "failed"
    assert result["failed_agent"] == "03"
    assert "contract_handoff_mismatch" in str(result["reason"])

    traces = result["stages"]
    assert traces[-1]["agent_id"] == "03"
    assert traces[-1]["checks"]["contract_handoff_match"] is False


@pytest.mark.integration
def test_pipeline_with_proposal_profile_generates_assessment_doc(tmp_path: Path) -> None:
    pipeline = EngineeringPipeline(tmp_path)
    profile = {
        "proposal_present": True,
        "project_type": "hibrido",
        "estimated_duration_weeks": {"min": 4, "avg": 7, "max": 10},
        "key_features": ["Client proposal intake", "Feasibility scoring", "Professional documentation output"],
        "recommended_stack": ["Python 3.11", "FastAPI", "React", "PostgreSQL"],
        "integrations": ["github", "sonarqube"],
        "missing_information": ["budget", "success_metrics"],
        "value_hypothesis": "Improve qualification quality before project commitment.",
    }

    result = pipeline.run(
        project="proposal-gamma",
        cycle=1,
        mode="autopilot_safe",
        proposal_profile=profile,
        proposal_text="Projeto para validar propostas de clientes com qualidade.",
        proposal_file="proposals/gamma.md",
    )

    assert result["status"] == "success"
    assert (tmp_path / "docs" / "26_proposta_avaliacao.md").exists()
    assert (tmp_path / "docs" / "27_descoberta_guiada.md").exists()
    assert (tmp_path / "docs" / "28_validacao_pre_kickoff.md").exists()


@pytest.mark.integration
def test_pipeline_with_vague_proposal_generates_discovery_gates(tmp_path: Path) -> None:
    pipeline = EngineeringPipeline(tmp_path)
    proposal_text = "Quero um app para meu negocio. Ainda nao sei exatamente o escopo."
    profile = build_proposal_profile("proposal-vaga", proposal_text)

    result = pipeline.run(
        project="proposal-vaga",
        cycle=1,
        mode="autopilot_safe",
        proposal_profile=profile,
        proposal_text=proposal_text,
        proposal_file="proposals/vaga.md",
    )

    assert result["status"] == "success"
    discovery_doc = tmp_path / "docs" / "27_descoberta_guiada.md"
    pre_kickoff_doc = tmp_path / "docs" / "28_validacao_pre_kickoff.md"
    assert discovery_doc.exists()
    assert pre_kickoff_doc.exists()

    discovery_content = discovery_doc.read_text(encoding="utf-8").lower()
    pre_kickoff_content = pre_kickoff_doc.read_text(encoding="utf-8").lower()
    assert "ambiguidade: alta" in discovery_content
    assert "kickoff_ready: false" in pre_kickoff_content
