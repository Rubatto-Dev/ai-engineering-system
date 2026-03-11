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

    def design(self, project: str, project_type: str) -> list[dict[str, str]]:
        track = {
            "frontend": "experiencia de interface, responsividade e conversao",
            "backend": "contratos de API, seguranca e confiabilidade de servicos",
            "automacao": "idempotencia, observabilidade e tolerancia a falhas",
            "hibrido": "integracao entre camadas com entrega incremental",
        }.get(project_type, "integracao entre camadas com entrega incremental")
        return [
            {
                "name": "MVP",
                "description": f"Build core {project} flow with minimum risk and short cycle.",
            },
            {
                "name": "Balanced",
                "description": f"Deliver {project} with modular architecture, {track}, and incremental rollout.",
            },
            {
                "name": "Scale-Ready",
                "description": f"Deliver {project} with scalability, observability, and security hardening.",
            },
        ]

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Intake for project=%s", context.project)
        proposal_profile = state.get("proposal_profile", {})
        project_type = str(proposal_profile.get("project_type", "hibrido"))
        scenarios = self.design(context.project, project_type)

        default_questions = [
            "What are the mandatory integrations for day one?",
            "What are the non-negotiable quality metrics?",
            "What is the acceptable deployment risk envelope?",
        ]
        missing_info = proposal_profile.get("missing_information", [])
        questions = [f"How should we define {gap} before planning commitment?" for gap in missing_info[:4]]
        questions.extend(default_questions)
        questions = questions[:6]

        lines = ["# Fluxos", "", "## Cenarios"]
        for scenario in scenarios:
            lines.append(f"- {scenario['name']}: {scenario['description']}")
        lines.extend(
            [
                "",
                "## Classificacao Inicial",
                f"- trilha_principal: {project_type}",
                "",
                "## Perguntas",
                *[f"- {question}" for question in questions],
            ]
        )

        fluxos_path = self._write("docs/04_fluxos.md", "\n".join(lines))
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[fluxos_path],
            notes=f"generated_scenarios={len(scenarios)}",
            checks={"sequential_thinking_used": True, "project_type": project_type},
            outputs={"scenarios": scenarios, "intake_questions": questions},
            handoff="11",
        )
