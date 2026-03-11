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
        proposal_profile = state.get("proposal_profile", {})
        project_type = str(proposal_profile.get("project_type", "hibrido"))
        value_hypothesis = str(
            proposal_profile.get(
                "value_hypothesis",
                f"Deliver measurable engineering value for {context.project}.",
            )
        )
        duration = proposal_profile.get("estimated_duration_weeks", {"min": 4, "avg": 6, "max": 8})
        missing_info = proposal_profile.get("missing_information", [])
        assumptions = proposal_profile.get("assumptions", [])

        scope = [
            "In scope: discovery, requirements, architecture baseline, and validation gates",
            "In scope: backlog prioritization and execution readiness with professional documentation",
            "Out of scope: direct production deploy automation in v1",
            f"Risk focus: integration stability, security controls, and proposal feasibility for {project_type}",
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
                    "## Hipotese de Valor",
                    f"- {value_hypothesis}",
                    "",
                    "## Estimativa Inicial",
                    (
                        f"- duracao_media_semanas: {duration.get('avg', 6)} "
                        f"(faixa {duration.get('min', 4)}-{duration.get('max', 8)})"
                    ),
                    "",
                    "## Assuncoes",
                    *[f"- {item}" for item in assumptions],
                    "",
                    "## Pendencias de Discovery",
                    *[f"- {item}" for item in missing_info],
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
            checks={"scope_items": len(scope), "proposal_profile_loaded": bool(proposal_profile)},
            outputs={"scope": scope},
            handoff="10",
        )
