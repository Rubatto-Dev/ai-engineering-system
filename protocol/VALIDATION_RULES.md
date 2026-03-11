# Validation Rules

These rules define the mandatory checks that must pass before `JARVIS: SHIP` is allowed.

## Ship Gate Requirements

### 1. Test Pyramid (`tests_ok`)
All three test layers must pass:
- Unit (`tests/unit/`)
- Integration (`tests/integration/`)
- E2E (`tests/e2e/`)

### 2. Documentation Completeness (`docs_updated`)
All mandatory project documents must exist and be non-empty.

### 3. Security Checks (`security_checks_ok`)
Security controls and threat documentation must be up to date.

### 4. Quality Gate (`quality_gate_ok`)
Quality gate must be green with no blocking issues.

### 5. ADR Updated (`adr_updated`)
`docs/decisions/ADR-0001.md` must exist and remain valid.

## Stage Validation (Blocking)

Before moving from one agent to the next, the current stage must satisfy:
- `result_schema_ok = true`
- `contract_loaded = true`
- `contract_required_sections_ok = true`
- `contract_handoff_match = true`
- `handoff_packet_ok = true`
- `notes_present = true`
- `artifacts_exist = true`

If any item above fails:
1. Stage status changes to `failed`
2. Pipeline halts immediately
3. Next stage is not executed

## Ship Blocking Policy

If any check fails:
1. `JARVIS: SHIP` returns `ship_blocked`
2. Response includes which checks failed
3. Team must fix issues and re-run `JARVIS: AUDIT`
