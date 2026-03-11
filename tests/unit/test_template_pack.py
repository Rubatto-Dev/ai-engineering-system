from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering_os.repository import ensure_structure
from ai_engineering_os.template_pack import initialize_client_template_packet


@pytest.mark.unit
def test_initialize_client_template_packet_creates_all_files(tmp_path: Path) -> None:
    ensure_structure(tmp_path)

    result = initialize_client_template_packet(
        tmp_path,
        client_name="ACME Contabilidade",
        project_name="Portal de Documentos",
        owner_name="Guilherme",
    )

    output_dir = Path(result["output_dir"])
    assert output_dir.exists()
    assert len(result["created_files"]) == 7
    first_file = output_dir / "00_intake_proposta.md"
    assert first_file.exists()
    content = first_file.read_text(encoding="utf-8")
    assert "ACME Contabilidade" in content
    assert "Portal de Documentos" in content
    assert "{{CLIENT_NAME}}" not in content


@pytest.mark.unit
def test_initialize_client_template_packet_skips_existing_without_overwrite(tmp_path: Path) -> None:
    ensure_structure(tmp_path)

    first_run = initialize_client_template_packet(
        tmp_path,
        client_name="Cliente X",
        project_name="Projeto Y",
        owner_name="Equipe",
    )
    second_run = initialize_client_template_packet(
        tmp_path,
        client_name="Cliente X",
        project_name="Projeto Y",
        owner_name="Equipe",
    )

    assert len(first_run["created_files"]) == 7
    assert len(second_run["created_files"]) == 0
    assert len(second_run["skipped_files"]) == 7


@pytest.mark.unit
def test_initialize_client_template_packet_accepts_custom_output_dir(tmp_path: Path) -> None:
    ensure_structure(tmp_path)

    result = initialize_client_template_packet(
        tmp_path,
        client_name="Cliente Z",
        project_name="Projeto Z",
        output_dir="proposals/custom/zeta",
    )

    output_dir = Path(result["output_dir"])
    assert output_dir == (tmp_path / "proposals" / "custom" / "zeta")
    assert output_dir.exists()
