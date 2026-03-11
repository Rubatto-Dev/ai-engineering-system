from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.security")


class SecurityAgent(BaseAgent):
    agent_id = "13"
    agent_name = "Security Agent"
    stage = "Security Engineering"

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Security Agent for project=%s", context.project)
        controls = [
            "Authentication and authorization boundaries",
            "Rate limiting and abuse protection",
            "Secrets handling policy",
            "Audit log retention for critical operations",
        ]
        threats = [
            "Prompt injection through external integrations",
            "Privilege escalation in automation pathways",
            "Data tampering during deployment",
        ]

        security_path = self._write(
            "docs/08_seguranca.md",
            "\n".join(["# Seguranca", "", "## Controles", *[f"- {c}" for c in controls]]),
        )
        threats_path = self._write(
            "docs/15_security_threats.md",
            "\n".join(["# Security Threats", "", *[f"- {t}" for t in threats]]),
        )
        risk_append = self._append(
            "docs/09_riscos.md",
            "\n## Complemento de Seguranca\n" + "\n".join([f"- {t}" for t in threats]) + "\n",
        )

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[security_path, threats_path, risk_append],
            notes="security_controls_defined",
            checks={"security_ok": True},
            outputs={"security_controls": controls, "security_threats": threats},
            handoff="06",
        )
