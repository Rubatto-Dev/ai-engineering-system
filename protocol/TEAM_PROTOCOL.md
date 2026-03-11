# Team Protocol

## Source of Truth

`AI_ENGINEERING_OS.md` is the source of truth for behavior and operating rules.

## Pipeline Execution Rules

1. Agents run in strict sequence from `build_agent_team()`.
2. Pipeline halts immediately on any stage with `status=failed`.
3. No next stage is executed when `stage_validation_ok=false`.

## Handoff Rules

1. Every stage must publish `outputs.handoff_packet`.
2. `handoff_packet.to_agent_id` must match contract handoff.
3. Missing or invalid handoff packet blocks the pipeline.

## Validation Rules

1. Every stage must satisfy all mandatory validation checks.
2. `JARVIS: SHIP` is blocked when any gate check fails.
3. Release requires green tests, docs, security, quality gate and ADR.

## Engineering Standards

- SOLID
- Clean Architecture
- Clean Code
- API First
- Documentation Driven Development
