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
        proposal_profile = state.get("proposal_profile", {})
        metrics = self._build_metrics(proposal_profile, state)
        outcome = self.evaluate(metrics)
        feasibility = str(proposal_profile.get("feasibility", "media"))
        value_hypothesis = str(
            proposal_profile.get(
                "value_hypothesis",
                f"Deliver measurable engineering value for {context.project}.",
            )
        )
        duration = proposal_profile.get("estimated_duration_weeks", {"min": 4, "avg": 6, "max": 8})
        risks = proposal_profile.get("risks", ["No critical blockers identified with current data."])
        missing_info = proposal_profile.get("missing_information", [])
        stack = proposal_profile.get("recommended_stack", ["Python 3.11", "Pytest", "SonarQube"])
        features = proposal_profile.get("key_features", [])
        ambiguity_level = str(proposal_profile.get("ambiguity_level", "media"))
        ambiguity_score = float(proposal_profile.get("ambiguity_score", 0.55))
        kickoff_recommendation = str(proposal_profile.get("kickoff_recommendation", "discovery_required"))
        validation_checklist = proposal_profile.get("validation_checklist", [])
        discovery_questions = proposal_profile.get("discovery_questions", [])
        features_lines = [f"- {feature}" for feature in features] if isinstance(features, list) and features else ["- Nao informado"]
        stack_lines = [f"- {item}" for item in stack] if isinstance(stack, list) and stack else ["- Nao informado"]
        risks_lines = [f"- {risk}" for risk in risks] if isinstance(risks, list) and risks else ["- Nao informado"]
        missing_lines = [f"- {gap}" for gap in missing_info] if isinstance(missing_info, list) and missing_info else ["- Nenhuma"]
        checklist_lines = (
            [f"- {item}" for item in validation_checklist]
            if isinstance(validation_checklist, list) and validation_checklist
            else ["- Checklist pre-kickoff nao informado"]
        )
        discovery_lines = (
            [f"- {item}" for item in discovery_questions[:6]]
            if isinstance(discovery_questions, list) and discovery_questions
            else ["- Sem perguntas registradas"]
        )
        kickoff_ready = kickoff_recommendation == "ready_for_scope_lock" and outcome["decision"] == "GO"

        risks_doc = self._write(
            "docs/09_riscos.md",
            """
# Riscos

## Avaliacao Inicial

- decisao: {decision}
- score: {score}
- viabilidade: {feasibility}
- estimativa_semanas: {duration_min}-{duration_max}

## Riscos Identificados
{risks}
            """.format(
                decision=outcome["decision"],
                score=outcome["score"],
                feasibility=feasibility,
                duration_min=duration.get("min", 4),
                duration_max=duration.get("max", 8),
                risks="\n".join([f"- {risk}" for risk in risks]),
            ),
        )
        proposal_eval_doc = self._write(
            "docs/26_proposta_avaliacao.md",
            "\n".join(
                [
                    "# Avaliacao de Proposta",
                    "",
                    f"- projeto: {context.project}",
                    f"- decisao: {outcome['decision']}",
                    f"- score: {outcome['score']}",
                    f"- viabilidade: {feasibility}",
                    f"- ambiguidade: {ambiguity_level} (score {ambiguity_score:.2f})",
                    f"- valor_estimado_score: {proposal_profile.get('value_score', 0.62)}",
                    (
                        f"- duracao_estimada_semanas: {duration.get('min', 4)}-"
                        f"{duration.get('max', 8)} (media {duration.get('avg', 6)})"
                    ),
                    f"- recommendation: {kickoff_recommendation}",
                    f"- scope_lock_ready: {kickoff_ready}",
                    "",
                    "## Hipotese de Valor",
                    f"- {value_hypothesis}",
                    "",
                    "## Features Principais",
                    *features_lines,
                    "",
                    "## Stack Recomendada",
                    *stack_lines,
                    "",
                    "## Riscos",
                    *risks_lines,
                    "",
                    "## Informacoes Pendentes",
                    *missing_lines,
                    "",
                    "## Perguntas de Discovery",
                    *discovery_lines,
                    "",
                    "## Checklist Pre-Kickoff",
                    *checklist_lines,
                ]
            ),
        )

        status = "success" if outcome["decision"] != "NO_GO" else "failed"
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status=status,
            artifacts=[risks_doc, proposal_eval_doc],
            notes=f"decision={outcome['decision']} score={outcome['score']}",
            checks={
                "decision": outcome["decision"],
                "proposal_profile_loaded": bool(proposal_profile),
                "kickoff_ready": kickoff_ready,
            },
            outputs={
                "idea_decision": outcome["decision"],
                "idea_score": outcome["score"],
                "kickoff_ready": kickoff_ready,
                "kickoff_recommendation": kickoff_recommendation,
            },
            handoff="08",
        )

    def _build_metrics(self, proposal_profile: Any, state: dict[str, Any]) -> dict[str, float]:
        if isinstance(proposal_profile, dict) and proposal_profile:
            complexity = float(proposal_profile.get("complexity_score", 0.35))
            clarity = float(proposal_profile.get("clarity_score", 0.80))
            integrations = proposal_profile.get("integrations", [])
            missing_info = proposal_profile.get("missing_information", [])
            dependency_risk = min(0.85, 0.20 + len(integrations) * 0.08) if isinstance(integrations, list) else 0.30
            operational_risk = min(0.90, 0.18 + len(missing_info) * 0.06) if isinstance(missing_info, list) else 0.30
            confidence = str(proposal_profile.get("confidence", "media"))
            confidence_boost = {"alta": 0.85, "media": 0.70, "baixa": 0.55}.get(confidence, 0.70)
            return {
                "clarity": clarity,
                "complexity": complexity,
                "dependency_risk": dependency_risk,
                "operational_risk": operational_risk,
                "time_confidence": confidence_boost,
                "cost_confidence": confidence_boost - 0.05,
            }

        return state.get(
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
