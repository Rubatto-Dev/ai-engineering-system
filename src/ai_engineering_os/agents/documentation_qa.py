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
        validation_path = self._write(
            "docs/11_validacao.md",
            "\n".join(
                [
                    "# Validacao",
                    "",
                    f"- ok: {qa['ok']}",
                    f"- missing: {len(qa['missing'])}",
                    f"- empty: {len(qa['empty'])}",
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
            artifacts=[validation_path],
            notes="documentation_validation_complete",
            checks=qa,
            outputs={"docs_qa": qa, "docs_qa_ok": qa["ok"]},
            handoff="09",
        )
