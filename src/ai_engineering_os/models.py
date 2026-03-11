from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StageTrace:
    stage: str
    status: str
    agent_id: str = ""
    agent_name: str = ""
    artifacts: list[str] = field(default_factory=list)
    notes: str = ""
    checks: dict[str, Any] = field(default_factory=dict)
    handoff: str = ""


@dataclass
class AgentResult:
    agent_id: str
    agent_name: str
    stage: str
    status: str
    artifacts: list[str] = field(default_factory=list)
    notes: str = ""
    checks: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    handoff: str = ""

    def to_trace(self) -> StageTrace:
        return StageTrace(
            stage=self.stage,
            status=self.status,
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            artifacts=self.artifacts,
            notes=self.notes,
            checks=self.checks,
            handoff=self.handoff,
        )


@dataclass
class ProjectContext:
    project: str
    cycle: int
    mode: str
    metadata: dict[str, Any] = field(default_factory=dict)