# Output Standard

Every agent stage MUST produce output following this standard format. Deviations will cause pipeline failures.

## Standard Output Schema

```json
{
  "agent_id": "00",
  "agent_name": "Idea Validator",
  "stage": "Idea Validator",
  "status": "success | warning | failed",
  "artifacts": ["docs/09_riscos.md"],
  "notes": "decision=GO score=0.7588",
  "checks": {"decision": "GO"},
  "outputs": {"idea_decision": "GO", "idea_score": 0.7588},
  "handoff": "08"
}
```

## Field Definitions

| Field | Type | Required | Description |
|---|---|---|---|
| `agent_id` | string | ✅ | Unique agent identifier (00-14) |
| `agent_name` | string | ✅ | Human-readable agent name |
| `stage` | string | ✅ | Pipeline stage name |
| `status` | enum | ✅ | `success`, `warning`, or `failed` |
| `artifacts` | list[string] | ✅ | Paths to files created/modified |
| `notes` | string | ✅ | Objective observations (machine-parseable preferred) |
| `checks` | dict | ✅ | Result of local validations |
| `outputs` | dict | ✅ | Key-value pairs added to pipeline state |
| `handoff` | string | ✅ | ID of the next agent, empty string if last |

## Status Values

| Status | Meaning | Pipeline Effect |
|---|---|---|
| `success` | Stage completed normally | Continue to next agent |
| `warning` | Stage completed with concerns | Continue but log warning |
| `failed` | Stage could not complete | Pipeline halts immediately |

## Artifact Paths
- All artifact paths are relative to `repo_root`
- Agents may create new files or append to existing ones
- Created files must be in `docs/`, `memory/`, or `schemas/` directories

## Examples

### Successful Stage
```json
{
  "agent_id": "04",
  "agent_name": "Software Architect",
  "stage": "Architecture Design",
  "status": "success",
  "artifacts": ["docs/05_arquitetura.md", "docs/07_api.md"],
  "notes": "architecture_and_api_written",
  "checks": {"context7_used": true, "layer_count": 4},
  "outputs": {"layers": ["entrypoints", "application", "domain", "infrastructure"]},
  "handoff": "05"
}
```

### Failed Stage
```json
{
  "agent_id": "07",
  "agent_name": "Documentation QA",
  "stage": "Documentation QA",
  "status": "failed",
  "artifacts": ["docs/11_validacao.md"],
  "notes": "documentation_validation_failed: 2 docs missing",
  "checks": {"ok": false, "missing": ["docs/07_api.md", "docs/13_deploy.md"]},
  "outputs": {"docs_qa_ok": false},
  "handoff": "09"
}
```
