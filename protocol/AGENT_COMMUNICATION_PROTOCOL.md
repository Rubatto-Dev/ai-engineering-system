# Agent Communication Protocol

Defines how agents exchange data, handle errors, and pass control in the pipeline.

## Communication Contract

### Input Contract
Every agent receives:
```python
def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
```

| Parameter | Type | Description |
|---|---|---|
| `context` | `ProjectContext` | Immutable project metadata (name, cycle, mode) |
| `state` | `dict` | Mutable shared state accumulated by all previous agents |

### Output Contract
Every agent returns an `AgentResult`:
```python
@dataclass
class AgentResult:
    agent_id: str           # "00" to "14"
    agent_name: str         # Human-readable name
    stage: str              # Pipeline stage name
    status: str             # "success" | "warning" | "failed"
    artifacts: list[str]    # Paths to created/modified files
    notes: str              # Machine-parseable observations
    checks: dict            # Local validation results
    outputs: dict           # Key-value pairs merged into state
    handoff: str            # Next agent's ID
```

### Error Contract
When an agent encounters a non-recoverable error:
```python
class AgentExecutionError(RuntimeError):
    """Raised when an agent fails with a non-recoverable issue."""
```

Error handling rules:
1. Set `status = "failed"` and describe the issue in `notes`
2. Pipeline orchestrator catches the failure and halts
3. The `notes` field must contain the cause AND recommended action
4. Partial artifacts may still be generated for debugging

## State Management

### State Flow
```
Agent 00 outputs → merged into state →
Agent 08 reads state + adds outputs → merged into state →
Agent 01 reads state + adds outputs → merged into state →
... (continues for all 16 agents)
```

### State Keys Convention
- Keys are descriptive: `idea_decision`, `functional_requirements`, `memory_patterns`
- Values can be any JSON-serializable type
- Agents MUST NOT mutate keys set by other agents
- The `pipeline_summary` key is reserved for the pipeline orchestrator

## Handoff Rules

### Valid Handoff Chain
```
00 → 08(query) → 01 → 11 → 02 → 03 → 10 → 04 → 05 → 13 → 06 → 07 → 09 → 12 → 14 → 08(update)
```

### Handoff Validation
1. Each agent's `handoff` field must reference the next agent's ID
2. The last agent (08 update phase) has `handoff = ""` (empty)
3. Mismatched handoff values trigger a warning log but don't halt the pipeline

## MCP Tool Integration

### Context7 (Context Enrichment)
```python
class Context7Adapter:
    def lookup(self, topic: str) -> list[str]:
        """Returns references from Context7 for the given topic."""
```
Used by: Agent 04 (Architecture), Agent 08 (Memory Query)

### Sequential Thinking (Structured Reasoning)
```python
class SequentialThinkingAdapter:
    def decompose(self, objective: str, steps: list[str] | None = None) -> list[str]:
        """Decomposes an objective into ordered steps."""
```
Used by: Agent 07 (Documentation QA), Agent 11 (PM)

## Data Serialization
- All data exchanged between agents is dict-serializable
- Artifact paths use forward slashes (POSIX-style)
- Text files use UTF-8 encoding
- Timestamps use UTC ISO-8601 format
