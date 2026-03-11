from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..models import AgentResult, ProjectContext
from ..repository import required_doc_paths
from .base import BaseAgent

logger = logging.getLogger("ai_engineering_os.agents.documentation_qa")


class DocumentationQaAgent(BaseAgent):
    agent_id = "07"
    agent_name = "Documentation QA"
    stage = "Documentation QA"

    def validate(self, required_docs: list[Path]) -> dict[str, object]:
        missing = [str(doc) for doc in required_docs if not doc.exists()]
        empty = [str(doc) for doc in required_docs if doc.exists() and not doc.read_text(encoding="utf-8").strip()]
        ok = not missing and not empty
        return {
            "ok": ok,
            "missing": missing,
            "empty": empty,
        }

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Documentation QA for project=%s", context.project)
        qa = self.validate(required_doc_paths(self.repo_root))
        proposal_profile = state.get("proposal_profile", {})
        proposal_required = isinstance(proposal_profile, dict) and bool(proposal_profile.get("proposal_present"))
        proposal_doc_ok = True
        discovery_doc_ok = True
        ambiguity_level = str(proposal_profile.get("ambiguity_level", "media")) if isinstance(proposal_profile, dict) else "media"
        missing_info = proposal_profile.get("missing_information", []) if isinstance(proposal_profile, dict) else []
        if not isinstance(missing_info, list):
            missing_info = []
        idea_decision = str(state.get("idea_decision", "UNKNOWN"))
        kickoff_recommendation = str(
            state.get(
                "kickoff_recommendation",
                proposal_profile.get("kickoff_recommendation", "discovery_required")
                if isinstance(proposal_profile, dict)
                else "discovery_required",
            )
        )
        kickoff_ready_signal = bool(state.get("kickoff_ready", False))
        validation_checklist = proposal_profile.get("validation_checklist", []) if isinstance(proposal_profile, dict) else []
        checklist_lines = [f"- {item}" for item in validation_checklist] if isinstance(validation_checklist, list) else []
        if not checklist_lines:
            checklist_lines = ["- Checklist pre-kickoff nao informado."]
        gap_lines = [f"- {gap}" for gap in missing_info] if missing_info else ["- Nenhum gap em aberto."]
        if proposal_required:
            proposal_doc = self.repo_root / "docs" / "26_proposta_avaliacao.md"
            discovery_doc = self.repo_root / "docs" / "27_descoberta_guiada.md"
            proposal_doc_ok = proposal_doc.exists() and bool(proposal_doc.read_text(encoding="utf-8").strip())
            discovery_doc_ok = discovery_doc.exists() and bool(discovery_doc.read_text(encoding="utf-8").strip())
            qa["proposal_assessment_doc_ok"] = proposal_doc_ok
            qa["discovery_brief_doc_ok"] = discovery_doc_ok
            qa["ok"] = bool(qa["ok"]) and proposal_doc_ok and discovery_doc_ok
        discovery_gaps = len(missing_info)
        pre_kickoff_ready = bool(qa["ok"]) and kickoff_ready_signal and idea_decision != "NO_GO"
        recommendation = "ready_for_scope_lock" if pre_kickoff_ready else kickoff_recommendation
        pre_kickoff_path = self._write(
            "docs/28_validacao_pre_kickoff.md",
            "\n".join(
                [
                    "# Validacao Pre-Kickoff",
                    "",
                    f"- projeto: {context.project}",
                    f"- documentacao_ok: {qa['ok']}",
                    f"- proposta_doc_ok: {proposal_doc_ok}",
                    f"- discovery_doc_ok: {discovery_doc_ok}",
                    f"- idea_decision: {idea_decision}",
                    f"- ambiguidade: {ambiguity_level}",
                    f"- gaps_abertos: {discovery_gaps}",
                    f"- kickoff_ready: {pre_kickoff_ready}",
                    f"- recommendation: {recommendation}",
                    "",
                    "## Checklist de Validacao",
                    *checklist_lines,
                    "",
                    "## Gaps em Aberto",
                    *gap_lines,
                ]
            ),
        )
        validation_path = self._write(
            "docs/11_validacao.md",
            "\n".join(
                [
                    "# Validacao",
                    "",
                    f"- ok: {qa['ok']}",
                    f"- missing: {len(qa['missing'])}",
                    f"- empty: {len(qa['empty'])}",
                    f"- proposal_assessment_doc_ok: {proposal_doc_ok}",
                    f"- discovery_brief_doc_ok: {discovery_doc_ok}",
                    f"- pre_kickoff_ready: {pre_kickoff_ready}",
                    "",
                    "## Sequential Thinking Trace",
                    *self.sequential.decompose(
                        "Validate documentation consistency",
                        [
                            "Collect required documents",
                            "Check presence and non-empty content",
                            "Record findings and unresolved issues",
                            "Publish validation summary",
                        ],
                    ),
                ]
            ),
        )

        status = "success" if qa["ok"] else "failed"
        logger.info("Documentation QA result: ok=%s missing=%d empty=%d", qa["ok"], len(qa["missing"]), len(qa["empty"]))
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status=status,
            artifacts=[validation_path, pre_kickoff_path],
            notes="documentation_validation_complete",
            checks={**qa, "pre_kickoff_ready": pre_kickoff_ready},
            outputs={
                "docs_qa": qa,
                "docs_qa_ok": qa["ok"],
                "pre_kickoff_ready": pre_kickoff_ready,
                "pre_kickoff_recommendation": recommendation,
            },
            handoff="09",
        )
