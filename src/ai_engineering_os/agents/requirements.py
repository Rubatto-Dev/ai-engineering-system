from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.requirements")


class RequirementsEngineerAgent(BaseAgent):
    agent_id = "02"
    agent_name = "Requirements Engineer"
    stage = "Requirements Engineering"

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Requirements Engineer for project=%s", context.project)
        proposal_profile = state.get("proposal_profile", {})
        key_features = proposal_profile.get("key_features", [])
        missing_info = proposal_profile.get("missing_information", [])
        duration = proposal_profile.get("estimated_duration_weeks", {"avg": 6})
        project_type = str(proposal_profile.get("project_type", "hibrido"))

        if isinstance(key_features, list) and key_features:
            functional = [f"Implementar feature prioritaria: {feature}" for feature in key_features[:5]]
        else:
            functional = [
                f"Allow orchestrated execution of all agents for {context.project}",
                "Persist generated artifacts with full traceability",
                "Expose Jarvis command protocol for start/plan/exec/audit/ship",
            ]

        non_functional = [
            "Test pyramid with unit, integration, and e2e coverage",
            "Quality gate checks before ship",
            "Auditability of each stage output",
            f"Planning confidence aligned with average duration target of {duration.get('avg', 6)} weeks",
            f"Delivery track controls for {project_type}",
        ]
        if isinstance(missing_info, list) and missing_info:
            non_functional.append("Open proposal discovery gaps must be closed before execution commitment")
        business_rules = [
            "No ship when any gate check fails",
            "Every stage must publish a handoff",
            "Critical changes require explicit audit result",
            "Proposal value, feasibility, and estimate must be documented before scope lock",
        ]

        req_path = self._write(
            "docs/02_requisitos.md",
            "\n".join(
                [
                    "# Requisitos",
                    "",
                    "## Funcionais",
                    *[f"- {item}" for item in functional],
                    "",
                    "## Nao Funcionais",
                    *[f"- {item}" for item in non_functional],
                ]
            ),
        )
        rules_path = self._write(
            "docs/03_regras_de_negocio.md",
            "\n".join(["# Regras de Negocio", "", *[f"- {rule}" for rule in business_rules]]),
        )

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[req_path, rules_path],
            notes="requirements_and_rules_written",
            checks={"requirements_count": len(functional) + len(non_functional)},
            outputs={
                "functional_requirements": functional,
                "non_functional_requirements": non_functional,
                "business_rules": business_rules,
                "project_type": project_type,
                "duration_estimate_weeks": duration,
            },
            handoff="03",
        )
