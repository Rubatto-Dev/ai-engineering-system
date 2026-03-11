from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

from .repository import ensure_structure, required_template_packet_paths


def initialize_client_template_packet(
    repo_root: Path,
    *,
    client_name: str,
    project_name: str,
    owner_name: str = "equipe",
    output_dir: str | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    ensure_structure(repo_root)

    client_slug = _slugify(client_name or "cliente")
    project_slug = _slugify(project_name or "projeto")
    target_dir = repo_root / output_dir if output_dir else repo_root / "proposals" / "packets" / f"{client_slug}_{project_slug}"
    target_dir.mkdir(parents=True, exist_ok=True)

    replacements = {
        "{{CLIENT_NAME}}": client_name or "cliente",
        "{{PROJECT_NAME}}": project_name or "projeto",
        "{{OWNER_NAME}}": owner_name or "equipe",
        "{{CREATED_AT_UTC}}": datetime.now(timezone.utc).isoformat(),
    }

    created: list[str] = []
    skipped: list[str] = []
    for template_path in required_template_packet_paths(repo_root):
        text = template_path.read_text(encoding="utf-8-sig")
        rendered = _apply_replacements(text, replacements)
        output_path = target_dir / template_path.name
        if output_path.exists() and not overwrite:
            skipped.append(str(output_path))
            continue
        output_path.write_text(rendered, encoding="utf-8")
        created.append(str(output_path))

    return {
        "output_dir": str(target_dir),
        "client_name": client_name,
        "project_name": project_name,
        "owner_name": owner_name,
        "created_files": created,
        "skipped_files": skipped,
    }


def _apply_replacements(text: str, replacements: dict[str, str]) -> str:
    rendered = text
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def _slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-") or "item"
