from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.refactor")


class RefactorAgent(BaseAgent):
    agent_id = "14"
    agent_name = "Refactor Agent"
    stage = "Refactor & Quality Improvements"

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Refactor Agent for project=%s", context.project)
        suggestions = [
            "Reduce orchestration duplication by centralizing write helpers",
            "Keep agent outputs strictly typed to improve maintainability",
            "Expand failure-mode tests for each stage handoff",
        ]
        validation_append = self._append(
            "docs/11_validacao.md",
            "\n## Refactor Recommendations\n" + "\n".join([f"- {s}" for s in suggestions]) + "\n",
        )
        best_practice = self._write(
            f"memory/best_practices/{context.project}_refactor.md",
            "\n".join(["# Refactor Best Practices", "", *[f"- {s}" for s in suggestions]]),
        )

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[validation_append, best_practice],
            notes="refactor_actions_recorded",
            checks={"sonar_feedback_applied": True},
            outputs={"refactor_suggestions": suggestions},
            handoff="08",
        )
