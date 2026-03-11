from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from .agents import build_agent_team
from .models import ProjectContext, StageTrace
from .repository import ensure_structure


class EngineeringPipeline:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def plan_steps(self) -> list[str]:
        ensure_structure(self.repo_root)
        return [agent.stage for agent in build_agent_team(self.repo_root)]

    def run(
        self,
        project: str,
        cycle: int,
        mode: str,
        proposal_profile: dict[str, object] | None = None,
        proposal_text: str | None = None,
        proposal_file: str | None = None,
    ) -> dict[str, object]:
        ensure_structure(self.repo_root)
        context = ProjectContext(project=project, cycle=cycle, mode=mode)
        team = build_agent_team(self.repo_root)

        traces: list[StageTrace] = []
        artifact_set: set[str] = set()
        state: dict[str, object] = {
            "pipeline_summary": "Pipeline started.",
            "tooling": {
                "context7": "enabled",
                "sequential_thinking": "enabled",
                "sonarqube": "configured",
            },
            "proposal_profile": proposal_profile or {},
            "proposal_text": proposal_text or "",
            "proposal_file": proposal_file,
        }

        for agent in team:
            result = agent.run(context, state)
            result = agent.enforce_contract(result)
            state.update(result.outputs)
            traces.append(result.to_trace())
            artifact_set.update(result.artifacts)
            state["pipeline_summary"] = f"Pipeline executed through: {result.stage}."

            if result.status == "failed":
                state["pipeline_summary"] = f"Pipeline stopped at agent {result.agent_id}."
                return {
                    "status": "failed",
                    "project": context.project,
                    "cycle": context.cycle,
                    "mode": context.mode,
                    "failed_agent": result.agent_id,
                    "reason": result.notes,
                    "stages": [asdict(trace) for trace in traces],
                    "artifacts": sorted(artifact_set),
                    "tooling": state["tooling"],
                }

        state["pipeline_summary"] = "Pipeline executed with all mandatory agents (00-14)."
        return {
            "status": "success",
            "project": context.project,
            "cycle": context.cycle,
            "mode": context.mode,
            "stages": [asdict(trace) for trace in traces],
            "artifacts": sorted(artifact_set),
            "tooling": state["tooling"],
            "agent_count": len({trace.agent_id for trace in traces if trace.agent_id}),
        }
