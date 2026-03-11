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

    def generate(self, project: str) -> list[BacklogItem]:
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
        items = self.generate(context.project)
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
