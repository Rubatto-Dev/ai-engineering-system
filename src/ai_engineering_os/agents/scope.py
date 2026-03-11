from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.scope")


class ScopeDefinitionAgent(BaseAgent):
    agent_id = "03"
    agent_name = "Scope Definition"
    stage = "Scope Definition"

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Scope Definition for project=%s", context.project)
        reqs = state.get("functional_requirements", [])
        scope = [
            "In scope: orchestration, documentation, quality gate, testing",
            "Out of scope: direct production deploy automation in v1",
            "Risk focus: integration stability and security controls",
        ]
        visao_path = self._write(
            "docs/01_visao.md",
            "\n".join(
                [
                    "# Visao",
                    "",
                    f"Projeto: {context.project}",
                    f"Ciclo: {context.cycle}",
                    f"Modo: {context.mode}",
                    "",
                    "## Escopo",
                    *[f"- {item}" for item in scope],
                    "",
                    "## Base de Requisitos",
                    *[f"- {item}" for item in reqs],
                ]
            ),
        )

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[visao_path],
            notes="scope_defined",
            checks={"scope_items": len(scope)},
            outputs={"scope": scope},
            handoff="10",
        )
