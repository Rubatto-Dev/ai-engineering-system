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
        base_entities = [
            "project",
            "agent_execution",
            "artifact",
            "quality_gate_report",
            "memory_record",
        ]
        proposal_profile = state.get("proposal_profile", {})
        features = proposal_profile.get("key_features", [])
        domain_entities: list[str] = []
        if isinstance(features, list):
            for feature in features[:4]:
                token = str(feature).lower()
                candidate = token.split(":")[0].split(",")[0].strip()
                candidate = candidate.replace(" ", "_")
                candidate = "".join(ch for ch in candidate if ch.isalnum() or ch == "_")
                if len(candidate) >= 5:
                    domain_entities.append(candidate[:40])
        entities = list(dict.fromkeys(base_entities + domain_entities))

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
