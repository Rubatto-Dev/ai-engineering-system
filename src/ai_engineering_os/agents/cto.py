from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.cto")


class CtoAgent(BaseAgent):
    agent_id = "10"
    agent_name = "CTO Agent"
    stage = "Technical Governance"

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running CTO Agent for project=%s", context.project)
        proposal_profile = state.get("proposal_profile", {})
        stack = proposal_profile.get("recommended_stack", ["Python 3.11", "Pytest", "SonarQube", "MCP adapters"])
        if not isinstance(stack, list) or not stack:
            stack = ["Python 3.11", "Pytest", "SonarQube", "MCP adapters", "Structured docs"]
        project_type = str(proposal_profile.get("project_type", "hibrido"))
        feasibility = str(proposal_profile.get("feasibility", "media"))
        adr1 = self._write(
            "docs/decisions/ADR-0001.md",
            "\n".join(
                [
                    "# ADR-0001",
                    "",
                    "## Context",
                    "Need deterministic AI engineering orchestration with strong validation.",
                    "",
                    "## Decision",
                    "Adopt Python orchestration with explicit multi-agent handoff and quality gate enforcement.",
                    "",
                    "## Consequences",
                    "Improved auditability and easier testability of pipeline behavior.",
                    f"Selected technical track: {project_type}.",
                    f"Feasibility level at decision time: {feasibility}.",
                ]
            ),
        )
        adr2 = self._write(
            "docs/decisions/ADR-0002.md",
            "\n".join(
                [
                    "# ADR-0002",
                    "",
                    "## Decision",
                    "Use staged deployment strategy controlled by SRE agent and SHIP gate.",
                ]
            ),
        )

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[adr1, adr2],
            notes="technical_decisions_published",
            checks={"adr_updated": True},
            outputs={"approved_stack": stack},
            handoff="04",
        )
