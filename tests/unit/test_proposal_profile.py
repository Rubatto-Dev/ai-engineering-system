from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering_os.proposal_profile import build_proposal_profile, load_proposal_text


@pytest.mark.unit
def test_build_proposal_profile_extracts_core_dimensions() -> None:
    text = """
Objetivo: Criar automacao para qualificar leads e enviar propostas.
- Integrar com WhatsApp, HubSpot e Stripe
- Dashboard web para acompanhar conversao
- API para sincronizar dados com CRM
Prazo: 8 semanas
KPI: aumentar taxa de conversao em 20%
"""
    profile = build_proposal_profile("cliente-alpha", text)

    assert profile["proposal_present"] is True
    assert profile["project_type"] in {"automacao", "hibrido", "backend", "frontend"}
    assert isinstance(profile["recommended_stack"], list)
    assert profile["estimated_duration_weeks"]["avg"] >= 2
    assert isinstance(profile["key_features"], list)
    assert isinstance(profile["missing_information"], list)
    assert profile["feasibility"] in {"alta", "media", "baixa"}


@pytest.mark.unit
def test_build_proposal_profile_defaults_when_no_text() -> None:
    profile = build_proposal_profile("cliente-beta", None)

    assert profile["proposal_present"] is False
    assert profile["source"] == "default_assumptions"
    assert profile["estimated_duration_weeks"]["avg"] >= 2


@pytest.mark.unit
def test_load_proposal_text_reads_relative_file(tmp_path: Path) -> None:
    repo_root = tmp_path
    proposal_path = repo_root / "proposals" / "brief.md"
    proposal_path.parent.mkdir(parents=True, exist_ok=True)
    proposal_path.write_text("Projeto com foco em API e dashboard.", encoding="utf-8")

    relative_path, text = load_proposal_text(repo_root, "proposals/brief.md")

    assert relative_path == "proposals\\brief.md" or relative_path == "proposals/brief.md"
    assert text == "Projeto com foco em API e dashboard."
