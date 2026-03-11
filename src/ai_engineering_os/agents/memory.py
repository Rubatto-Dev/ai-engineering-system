from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..memory_store import GlobalMemoryStore
from ..models import AgentResult, ProjectContext
from .base import BaseAgent, Context7Adapter, SequentialThinkingAdapter

logger = logging.getLogger("ai_engineering_os.agents.memory")


class GlobalMemoryAgent(BaseAgent):
    agent_id = "08"
    agent_name = "Global Engineering Memory"

    def __init__(
        self,
        repo_root: Path,
        context7: Context7Adapter,
        sequential: SequentialThinkingAdapter,
        memory_store: GlobalMemoryStore,
        phase: str,
    ) -> None:
        super().__init__(repo_root, context7, sequential, memory_store)
        if phase not in {"query", "update"}:
            raise ValueError("phase must be 'query' or 'update'")
        self.phase = phase
        self.stage = "Global Memory Query" if phase == "query" else "Learning & Memory Update"

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        logger.info("Running Memory Agent phase=%s project=%s", self.phase, context.project)

        if self.phase == "query":
            hits = self.context7.lookup(f"{context.project} architecture and delivery patterns")
            pattern_path = self._write(
                f"memory/patterns/{context.project}_patterns.md",
                "\n".join(["# Patterns", "", *[f"- {hit}" for hit in hits]]),
            )
            return AgentResult(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                stage=self.stage,
                status="success",
                artifacts=[pattern_path],
                notes=f"patterns_loaded={len(hits)}",
                checks={"context7_used": True},
                outputs={"memory_patterns": hits},
                handoff="01",
            )

        summary = state.get("pipeline_summary", "Pipeline executed with all mandatory agents.")
        project_record = self.memory_store.record_project(context.project, summary)
        lesson_text = state.get(
            "learning_note",
            "Use strict stage handoff and quality-gate checks before ship.",
        )
        lesson_record = self.memory_store.record_lesson(context.project, lesson_text)
        logger.info("Memory updated: project=%s", context.project)
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            stage=self.stage,
            status="success",
            artifacts=[str(project_record), str(lesson_record)],
            notes="memory_updated",
            checks={"memory_write": True},
            outputs={"memory_updated": True},
            handoff="",
        )
