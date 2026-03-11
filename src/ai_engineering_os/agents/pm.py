from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.pm")


class ProjectManagerAgent(BaseAgent):
    agent_id = "11"
    agent_name = "Project Manager Agent"
    stage = "Planning"

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Project Manager for project=%s", context.project)
        proposal_profile = state.get("proposal_profile", {})
        duration = proposal_profile.get("estimated_duration_weeks", {"avg": 6})
        project_type = str(proposal_profile.get("project_type", "hibrido"))
        milestones = self.sequential.decompose(
            f"Roadmap for {context.project}",
            [
                f"Finalize discovery and value validation for {project_type} track",
                "Finalize requirements and architecture baseline",
                "Implement core orchestration and test pyramid",
                "Integrate quality gate and external tooling",
                "Perform audit and prepare release",
            ],
        )
        timeline_hint = (
            f"- estimated_duration_weeks: {duration.get('min', 4)}-"
            f"{duration.get('max', 8)} (avg {duration.get('avg', 6)})"
        )
        roadmap_path = self._write(
            "docs/12_roadmap.md",
            "\n".join(["# Roadmap", "", "## Milestones", *[f"- {m}" for m in milestones], "", "## Timeline", timeline_hint]),
        )

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[roadmap_path],
            notes=f"milestones={len(milestones)}",
            checks={"sequential_thinking_used": True},
            outputs={"roadmap_milestones": milestones},
            handoff="02",
        )
