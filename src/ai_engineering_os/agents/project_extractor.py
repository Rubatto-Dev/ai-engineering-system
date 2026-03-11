from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.project_extractor")


class ProjectExtractorAgent(BaseAgent):
    agent_id = "09"
    agent_name = "Project Extractor"
    stage = "Project Extractor"

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Project Extractor for project=%s", context.project)
        source_files = [
            path
            for path in (self.repo_root / "src").rglob("*.py")
            if "__pycache__" not in str(path)
        ]
        summary = [
            "\n## Project Extractor Snapshot\n",
            f"- python_files: {len(source_files)}\n",
            "- api_contracts: docs/07_api.md\n",
            "- data_model: docs/06_modelo_dados.md\n",
            "- dependencies: pyproject.toml and package.json\n",
        ]
        validation_path = self._append("docs/11_validacao.md", "".join(summary))

        architecture_snapshot = self._write(
            f"memory/architectures/{context.project}_snapshot.md",
            "\n".join(
                [
                    "# Architecture Snapshot",
                    "",
                    f"- project: {context.project}",
                    f"- python_files: {len(source_files)}",
                    "- extracted_by: Agent 09",
                ]
            ),
        )

        logger.info("Extracted %d Python files", len(source_files))
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[validation_path, architecture_snapshot],
            notes="project_snapshot_recorded",
            checks={"python_files": len(source_files)},
            outputs={"project_python_file_count": len(source_files)},
            handoff="12",
        )
