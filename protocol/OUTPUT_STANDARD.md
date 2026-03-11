# Output Standard

Every agent stage must produce output in this format.

## Standard Output Schema

```json
{
  "agent_id": "00",
  "agent_name": "Idea Validator",
  "stage": "Idea Validator",
  "status": "success",
  "artifacts": ["docs/09_riscos.md"],
  "notes": "decision=GO score=0.7588",
  "checks": {
    "result_schema_ok": true,
    "contract_handoff_match": true,
    "handoff_packet_ok": true,
    "stage_validation_ok": true
  },
  "outputs": {
    "idea_decision": "GO",
    "idea_score": 0.7588,
    "handoff_packet": {
      "from_agent_id": "00",
      "to_agent_id": "08",
      "summary": "decision=GO score=0.7588",
      "validation_snapshot": {
        "result_schema_ok": true,
        "contract_loaded": true,
        "contract_required_sections_ok": true,
        "contract_handoff_match": true
      }
    }
  },
  "handoff": "08"
}
```

## Mandatory fields

- `agent_id`
- `agent_name`
- `stage`
- `status`
- `artifacts`
- `notes`
- `checks`
- `outputs`
- `handoff`

## Mandatory stage checks

- `checks.result_schema_ok = true`
- `checks.contract_loaded = true`
- `checks.contract_required_sections_ok = true`
- `checks.contract_handoff_match = true`
- `checks.handoff_packet_ok = true`
- `checks.stage_validation_ok = true`

If any mandatory check fails, stage status must be `failed` and pipeline must stop.
