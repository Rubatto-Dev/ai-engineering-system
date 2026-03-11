from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.architect")


class SoftwareArchitectAgent(BaseAgent):
    agent_id = "04"
    agent_name = "Software Architect"
    stage = "Architecture Design"

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Software Architect for project=%s", context.project)
        references = self.context7.lookup(f"{context.project} clean architecture api first")
        layers = ["entrypoints", "application", "domain", "infrastructure"]
        integrations = ["Trello MCP", "SonarQube MCP", "Context7 MCP", "Sequential Thinking MCP"]
        api_endpoints = [
            "POST /jarvis/start",
            "POST /jarvis/plan",
            "POST /jarvis/exec",
            "POST /jarvis/audit",
            "POST /jarvis/ship",
        ]

        arch_path = self._write(
            "docs/05_arquitetura.md",
            "\n".join(
                [
                    "# Arquitetura",
                    "",
                    "## Camadas",
                    *[f"- {layer}" for layer in layers],
                    "",
                    "## Integracoes",
                    *[f"- {integration}" for integration in integrations],
                    "",
                    "## Referencias Context7",
                    *[f"- {ref}" for ref in references],
                ]
            ),
        )

        api_path = self._write(
            "docs/07_api.md",
            "\n".join(["# API", "", "## Endpoints", *[f"- {ep}" for ep in api_endpoints]]),
        )

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[arch_path, api_path],
            notes="architecture_and_api_written",
            checks={"context7_used": True, "layer_count": len(layers)},
            outputs={"layers": layers, "integrations": integrations, "api_endpoints": api_endpoints},
            handoff="05",
        )
