# Agent Communication Protocol

Defines how agents exchange data, handle errors, and pass control in the pipeline.

## Communication Contract

### Input Contract

Every agent receives:

```python
def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
```

### Output Contract

Every agent returns an `AgentResult` with these mandatory fields:
- `agent_id`
- `agent_name`
- `stage`
- `status`
- `artifacts`
- `notes`
- `checks`
- `outputs`
- `handoff`

## State Management

### State Flow

`Agent 00 -> Agent 08(query) -> Agent 01 -> ... -> Agent 14 -> Agent 08(update)`

### State Rules

- Keys must be descriptive and JSON-serializable.
- Agents must not mutate keys owned by other agents.
- `pipeline_summary` is reserved for the orchestrator.

## Handoff Rules

1. Every stage must publish `outputs.handoff_packet`.
2. `handoff_packet.to_agent_id` must match the contract handoff.
3. Last stage uses `to_agent_id=""`.
4. Any mismatch blocks the pipeline.

## Validation Snapshot

Every stage must publish this minimum `handoff_packet` structure:

```json
{
  "from_agent_id": "03",
  "from_agent_name": "Scope Definition",
  "from_stage": "Scope Definition",
  "to_agent_id": "10",
  "status": "success",
  "summary": "scope_defined",
  "artifacts": ["docs/01_visao.md"],
  "open_questions": [],
  "assumptions": [],
  "risks": [],
  "validation_snapshot": {
    "result_schema_ok": true,
    "contract_loaded": true,
    "contract_required_sections_ok": true,
    "contract_handoff_match": true
  },
  "validated_at_utc": "2026-03-11T00:00:00+00:00"
}
```

Rules:
1. `handoff_packet` is mandatory.
2. `summary` must be non-empty.
3. `validation_snapshot` must be present and consistent with stage checks.
4. Missing fields set stage status to `failed`.
