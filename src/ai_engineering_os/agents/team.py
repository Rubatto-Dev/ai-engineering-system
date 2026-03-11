from __future__ import annotations

from pathlib import Path

from ..memory_store import GlobalMemoryStore
from .architect import SoftwareArchitectAgent
from .backlog import BacklogAgent
from .base import BaseAgent, Context7Adapter, SequentialThinkingAdapter
from .cto import CtoAgent
from .data_model import DataModelingAgent
from .documentation_qa import DocumentationQaAgent
from .idea_validator import IdeaValidatorAgent
from .intake import IntakeScenarioAgent
from .memory import GlobalMemoryAgent
from .pm import ProjectManagerAgent
from .project_extractor import ProjectExtractorAgent
from .refactor import RefactorAgent
from .requirements import RequirementsEngineerAgent
from .scope import ScopeDefinitionAgent
from .security import SecurityAgent
from .sre import SreAgent


def build_agent_team(repo_root: Path) -> list[BaseAgent]:
    context7 = Context7Adapter()
    sequential = SequentialThinkingAdapter()
    memory_store = GlobalMemoryStore(repo_root)

    return [
        IdeaValidatorAgent(repo_root, context7, sequential, memory_store),
        GlobalMemoryAgent(repo_root, context7, sequential, memory_store, phase="query"),
        IntakeScenarioAgent(repo_root, context7, sequential, memory_store),
        ProjectManagerAgent(repo_root, context7, sequential, memory_store),
        RequirementsEngineerAgent(repo_root, context7, sequential, memory_store),
        ScopeDefinitionAgent(repo_root, context7, sequential, memory_store),
        CtoAgent(repo_root, context7, sequential, memory_store),
        SoftwareArchitectAgent(repo_root, context7, sequential, memory_store),
        DataModelingAgent(repo_root, context7, sequential, memory_store),
        SecurityAgent(repo_root, context7, sequential, memory_store),
        BacklogAgent(repo_root, context7, sequential, memory_store),
        DocumentationQaAgent(repo_root, context7, sequential, memory_store),
        ProjectExtractorAgent(repo_root, context7, sequential, memory_store),
        SreAgent(repo_root, context7, sequential, memory_store),
        RefactorAgent(repo_root, context7, sequential, memory_store),
        GlobalMemoryAgent(repo_root, context7, sequential, memory_store, phase="update"),
    ]


def execution_stage_names() -> list[str]:
    return [agent.stage for agent in build_agent_team(Path("."))]
