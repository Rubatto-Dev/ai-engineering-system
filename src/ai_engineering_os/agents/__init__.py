"""Agent package - modular agent implementations for the AI Engineering OS pipeline."""

from .architect import SoftwareArchitectAgent
from .backlog import BacklogAgent
from .base import (
    AgentExecutionError,
    BacklogItem,
    BaseAgent,
    Context7Adapter,
    SequentialThinkingAdapter,
)
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
from .team import build_agent_team, execution_stage_names

__all__ = [
    "AgentExecutionError",
    "BacklogItem",
    "BaseAgent",
    "Context7Adapter",
    "SequentialThinkingAdapter",
    "IdeaValidatorAgent",
    "GlobalMemoryAgent",
    "IntakeScenarioAgent",
    "RequirementsEngineerAgent",
    "ScopeDefinitionAgent",
    "SoftwareArchitectAgent",
    "DataModelingAgent",
    "BacklogAgent",
    "DocumentationQaAgent",
    "ProjectExtractorAgent",
    "CtoAgent",
    "ProjectManagerAgent",
    "SreAgent",
    "SecurityAgent",
    "RefactorAgent",
    "build_agent_team",
    "execution_stage_names",
]
