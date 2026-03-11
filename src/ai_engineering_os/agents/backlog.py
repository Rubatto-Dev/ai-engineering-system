from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BacklogItem, BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.backlog")


class BacklogAgent(BaseAgent):
    agent_id = "06"
    agent_name = "Backlog Engineer"
    stage = "Backlog Generation"

    def generate(self, project: str, proposal_profile: dict[str, Any] | None = None) -> list[BacklogItem]:
        if proposal_profile:
            features = proposal_profile.get("key_features", [])
            duration = proposal_profile.get("estimated_duration_weeks", {"avg": 6})
            missing_info = proposal_profile.get("missing_information", [])
            ambiguity_level = str(proposal_profile.get("ambiguity_level", "media"))
            dynamic_items: list[BacklogItem] = []
            item_idx = 1

            if ambiguity_level == "alta" or (isinstance(missing_info, list) and missing_info):
                discovery_effort = 4 if ambiguity_level == "alta" else 3
                dynamic_items.append(
                    BacklogItem(
                        item_id=f"BL-{item_idx:03d}",
                        description="Conduzir discovery guiada e fechar gaps da proposta antes do scope lock",
                        priority="high",
                        effort=discovery_effort,
                        acceptance_criteria=[
                            "Perguntas prioritarias de discovery respondidas e aprovadas",
                            "Gaps criticos (prazo, budget, KPI, compliance) fechados ou com plano de mitigacao",
                        ],
                    )
                )
                item_idx += 1

            if isinstance(features, list) and features:
                for feature in features[:4]:
                    item_id = f"BL-{item_idx:03d}"
                    effort = max(2, min(8, int(duration.get("avg", 6) / 2)))
                    dynamic_items.append(
                        BacklogItem(
                            item_id=item_id,
                            description=f"Implement and validate: {feature}",
                            priority="high" if item_idx <= 2 else "medium",
                            effort=effort,
                            acceptance_criteria=[
                                f"Feature delivered for proposal objective: {feature}",
                                "Documentation and tests updated with traceability",
                            ],
                        )
                    )
                    item_idx += 1
            else:
                dynamic_items.append(
                    BacklogItem(
                        item_id=f"BL-{item_idx:03d}",
                        description="Definir e validar backlog MVP quando a proposta nao traz features detalhadas",
                        priority="high",
                        effort=3,
                        acceptance_criteria=[
                            "MVP com ate 5 funcionalidades priorizadas",
                            "Criterios de aceite definidos com stakeholders",
                        ],
                    )
                )
                item_idx += 1

            dynamic_items.append(
                BacklogItem(
                    item_id=f"BL-{item_idx:03d}",
                    description="Run feasibility, quality gate, and runtime validation before execution start",
                    priority="high",
                    effort=3,
                    acceptance_criteria=[
                        "test:python, quality:python, runtime:check all successful",
                        "Proposal evaluation and risk docs approved",
                    ],
                )
            )
            return dynamic_items

        return [
            BacklogItem(
                item_id="BL-001",
                description=f"Define and validate requirements for {project}",
                priority="high",
                effort=3,
                acceptance_criteria=[
                    "Functional requirements documented",
                    "Non-functional requirements documented",
                ],
            ),
            BacklogItem(
                item_id="BL-002",
                description="Implement architecture skeleton and API contracts",
                priority="high",
                effort=5,
                acceptance_criteria=[
                    "Architecture document updated",
                    "API spec drafted",
                ],
            ),
            BacklogItem(
                item_id="BL-003",
                description="Implement test pyramid and quality gate automation",
                priority="high",
                effort=5,
                acceptance_criteria=[
                    "Unit, integration, and e2e tests passing",
                    "Quality gate script returning success",
                ],
            ),
            BacklogItem(
                item_id="BL-004",
                description="Integrate Context7 and Sequential-Thinking in planning path",
                priority="medium",
                effort=3,
                acceptance_criteria=[
                    "Context enrichment is available",
                    "Sequential plan stored in validation docs",
                ],
            ),
        ]

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Backlog Engineer for project=%s", context.project)
        proposal_profile = state.get("proposal_profile", {})
        items = self.generate(context.project, proposal_profile if isinstance(proposal_profile, dict) else None)
        lines = ["# Backlog", ""]
        for item in items:
            lines.append(f"## {item.item_id} - {item.description}")
            lines.append(f"- priority: {item.priority}")
            lines.append(f"- effort: {item.effort}")
            lines.append("- acceptance_criteria:")
            for criterion in item.acceptance_criteria:
                lines.append(f"  - {criterion}")
            lines.append("")

        backlog_path = self._write("docs/10_backlog.md", "\n".join(lines))
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[backlog_path],
            notes=f"items={len(items)}",
            checks={"backlog_items": len(items)},
            outputs={"backlog_items": items, "backlog_count": len(items)},
            handoff="07",
        )
