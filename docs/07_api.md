# API

## Contrato de comando (Jarvis Protocol)

Formato de entrada:

- `JARVIS: START project=<name>`
- `JARVIS: PLAN cycle=<n>`
- `JARVIS: EXEC cycle=<n> mode=<advisor|builder|autopilot_safe|autopilot_full|audit>`
- `JARVIS: AUDIT repo=<name> [tests_ok=<bool>] [security_ok=<bool>] [sonar_ok=<bool>] [strict_external=<bool>]`
- `JARVIS: SHIP version=<semver>`

## Mapeamento logico de endpoints

- `POST /jarvis/start`
  - request: `{ "project": "alpha" }`
  - response principal: `{ "status": "started", "project": "alpha" }`
- `POST /jarvis/plan`
  - request: `{ "cycle": 1 }`
  - response principal: `{ "status": "planned", "steps": [...], "agents_expected": 15 }`
- `POST /jarvis/exec`
  - request: `{ "cycle": 1, "mode": "autopilot_safe" }`
  - response principal: `{ "status": "success|failed", "stages": [...], "artifacts": [...] }`
  - cada `stage` inclui checks de contrato, `handoff_packet_ok` e `stage_validation_ok`
- `POST /jarvis/audit`
  - request: `{ "repo": "alpha", "strict_external": true }`
  - response principal: `{ "status": "audit_ok|audit_failed", "result": { "checks": {...} } }`
- `POST /jarvis/ship`
  - request: `{ "version": "0.1.0" }`
  - response principal: `{ "status": "shipped|ship_blocked", "reason": "<when_blocked>" }`

## Regras de validacao de entrada

- Comandos suportados: `START`, `PLAN`, `EXEC`, `AUDIT`, `SHIP`.
- `cycle` deve ser inteiro positivo.
- `mode` deve estar no conjunto permitido.
- `START` exige `project`.
- `SHIP` exige `version`.

## Regras de bloqueio

- `SHIP` bloqueia sem `EXEC` previo.
- `SHIP` bloqueia sem `AUDIT` da ultima execucao.
- `SHIP` bloqueia se quality gate mudar para fail apos auditoria.
- `EXEC` bloqueia no primeiro stage com `stage_validation_ok=false`.
