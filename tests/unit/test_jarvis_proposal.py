from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering_os.jarvis import JarvisEngine


@pytest.mark.unit
def test_start_loads_proposal_profile_when_file_exists(tmp_path: Path) -> None:
    proposal = tmp_path / "proposals" / "cliente.md"
    proposal.parent.mkdir(parents=True, exist_ok=True)
    proposal.write_text(
        "\n".join(
            [
                "Objetivo: plataforma para captar leads e automatizar atendimento.",
                "- Integrar WhatsApp e CRM",
                "- API para parceiros",
                "- Dashboard web de indicadores",
                "Prazo: 10 semanas",
            ]
        ),
        encoding="utf-8",
    )
    engine = JarvisEngine(tmp_path)

    result = engine.handle("JARVIS: START project=alpha proposal_file=proposals/cliente.md")

    assert result["status"] == "started"
    assert result["proposal_loaded"] is True
    assert result["proposal_file"] in {"proposals/cliente.md", "proposals\\cliente.md"}
    profile = result["proposal_profile"]
    assert isinstance(profile, dict)
    assert profile["proposal_present"] is True
    assert profile["estimated_duration_weeks"]["avg"] >= 2


@pytest.mark.unit
def test_exec_with_proposal_generates_proposal_assessment_doc(tmp_path: Path) -> None:
    proposal = tmp_path / "proposal.txt"
    proposal.write_text("Objetivo: criar backend API com dashboard e automacao de notificacoes.", encoding="utf-8")
    engine = JarvisEngine(tmp_path)
    engine.handle("JARVIS: START project=alpha proposal_file=proposal.txt")

    result = engine.handle("JARVIS: EXEC cycle=1 mode=autopilot_safe")

    assert result["status"] == "success"
    assessment_doc = tmp_path / "docs" / "26_proposta_avaliacao.md"
    assert assessment_doc.exists()
    content = assessment_doc.read_text(encoding="utf-8")
    assert "Avaliacao de Proposta" in content
    assert "duracao_estimada_semanas" in content
