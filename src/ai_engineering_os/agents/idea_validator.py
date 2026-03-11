from __future__ import annotations

import logging
from typing import Any

from ..models import AgentResult, ProjectContext
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.idea_validator")


class IdeaValidatorAgent(BaseAgent):
    agent_id = "00"
    agent_name = "Idea Validator"
    stage = "Idea Validator"

    def evaluate(self, metrics: dict[str, float]) -> dict[str, str | float]:
        clarity = metrics.get("clarity", 0.7)
        complexity = metrics.get("complexity", 0.4)
        dependency_risk = metrics.get("dependency_risk", 0.3)
        operational_risk = metrics.get("operational_risk", 0.3)
        time_confidence = metrics.get("time_confidence", 0.7)
        cost_confidence = metrics.get("cost_confidence", 0.7)

        score = (
            clarity * 0.35
            + (1 - complexity) * 0.2
            + (1 - dependency_risk) * 0.15
            + (1 - operational_risk) * 0.15
            + time_confidence * 0.075
            + cost_confidence * 0.075
        )

        decision = "NO_GO"
        if score >= 0.75:
            decision = "GO"
        elif score >= 0.55:
            decision = "GO_COM_RESSALVAS"

        logger.info("Idea evaluation: decision=%s score=%.4f", decision, score)
        return {"decision": decision, "score": round(score, 4)}

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Idea Validator for project=%s", context.project)
        metrics = state.get(
            "idea_metrics",
            {
                "clarity": 0.85,
                "complexity": 0.35,
                "dependency_risk": 0.30,
                "operational_risk": 0.25,
                "time_confidence": 0.80,
                "cost_confidence": 0.75,
            },
        )
        outcome = self.evaluate(metrics)

        risks_doc = self._write(
            "docs/09_riscos.md",
            """
# Riscos

## Avaliacao Inicial

- decisao: {decision}
- score: {score}
- risco_operacional: monitorado
- risco_dependencias: monitorado
            """.format(decision=outcome["decision"], score=outcome["score"]),
        )

        status = "success" if outcome["decision"] != "NO_GO" else "failed"
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status=status,
            artifacts=[risks_doc],
            notes=f"decision={outcome['decision']} score={outcome['score']}",
            checks={"decision": outcome["decision"]},
            outputs={"idea_decision": outcome["decision"], "idea_score": outcome["score"]},
            handoff="08",
        )
