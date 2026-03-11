from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.sre")


class SreAgent(BaseAgent):
    agent_id = "12"
    agent_name = "SRE Agent"
    stage = "Testing & Deployment Readiness"

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running SRE Agent for project=%s", context.project)
        deploy_path = self._write(
            "docs/13_deploy.md",
            "\n".join(
                [
                    "# Deploy",
                    "",
                    "## Pipeline",
                    "- Build",
                    "- Unit/Integration/E2E tests",
                    "- SonarQube quality gate",
                    "- Controlled rollout",
                ]
            ),
        )
        observability_path = self._write(
            "docs/14_observability.md",
            "\n".join(
                [
                    "# Observability",
                    "",
                    "- Structured logs",
                    "- Trace correlation by cycle",
                    "- Agent stage latency",
                    "- Quality gate metrics",
                ]
            ),
        )

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[deploy_path, observability_path],
            notes="deploy_and_observability_ready",
            checks={"sonarqube_required": True},
            outputs={"sre_ready": True},
            handoff="14",
        )
