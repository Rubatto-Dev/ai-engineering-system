from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.data_model")


class DataModelingAgent(BaseAgent):
    agent_id = "05"
    agent_name = "Data Modeling"
    stage = "Data Modeling"

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Data Modeling for project=%s", context.project)
        entities = [
            "project",
            "agent_execution",
            "artifact",
            "quality_gate_report",
            "memory_record",
        ]

        model_path = self._write(
            "docs/06_modelo_dados.md",
            "\n".join(["# Modelo de Dados", "", "## Entidades", *[f"- {entity}" for entity in entities]]),
        )

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[model_path],
            notes="data_model_written",
            checks={"entity_count": len(entities)},
            outputs={"entities": entities},
            handoff="13",
        )
