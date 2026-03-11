from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.intake")


class IntakeScenarioAgent(BaseAgent):
    agent_id = "01"
    agent_name = "Intake & Scenario Designer"
    stage = "Intake & Scenario Design"

    def design(self, project: str) -> list[dict[str, str]]:
        return [
            {
                "name": "MVP",
                "description": f"Build core {project} flow with minimum risk and short cycle.",
            },
            {
                "name": "Balanced",
                "description": f"Deliver {project} with modular architecture and incremental rollout.",
            },
            {
                "name": "Scale-Ready",
                "description": f"Deliver {project} with scalability, observability, and security hardening.",
            },
        ]

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Intake for project=%s", context.project)
        scenarios = self.design(context.project)
        questions = [
            "What are the mandatory integrations for day one?",
            "What are the non-negotiable quality metrics?",
            "What is the acceptable deployment risk envelope?",
        ]

        lines = ["# Fluxos", "", "## Cenarios"]
        for scenario in scenarios:
            lines.append(f"- {scenario['name']}: {scenario['description']}")
        lines.extend(["", "## Perguntas", *[f"- {question}" for question in questions]])

        fluxos_path = self._write("docs/04_fluxos.md", "\n".join(lines))
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[fluxos_path],
            notes=f"generated_scenarios={len(scenarios)}",
            checks={"sequential_thinking_used": True},
            outputs={"scenarios": scenarios, "intake_questions": questions},
            handoff="11",
        )
