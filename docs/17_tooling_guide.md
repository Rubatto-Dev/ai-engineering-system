# Tooling Guide

## SonarQube

- Configure scanner with `sonar-project.properties`.
- Run analysis in CI before ship.
- Feed `sonar_ok` into `JARVIS: AUDIT`.
- Runtime endpoint expected by checks: `http://localhost:9000/api/system/status`.
- Start local SonarQube with `npm run sonar:up`.
- Stop local SonarQube with `npm run sonar:down`.

## Context7

- Use as context retrieval source before planning and architecture decisions.
- Persist relevant findings in `memory/patterns`.

## Sequential Thinking

- Use for stepwise decomposition of complex work.
- Persist reasoning checkpoints in `docs/11_validacao.md`.

## GitHub MCP

- The project MCP config now includes `github` with command `mcp-server-github`.
- Set a valid token in your shell before using GitHub MCP:
  - PowerShell (current session): `$env:GITHUB_PERSONAL_ACCESS_TOKEN="<NOVO_TOKEN>"`
  - PowerShell (persist for user): `[Environment]::SetEnvironmentVariable("GITHUB_PERSONAL_ACCESS_TOKEN","<NOVO_TOKEN>","User")`
- Test local startup with `npm run mcp:github`.
- Use GitHub MCP tools (`create_repository`, `push_files`, `create_pull_request`) to publish and update the agents project.
- Never store tokens in tracked files.

## Runtime Readiness

- Run `npm run runtime:check` to validate Node, npm, MCP runtime startup, and SonarQube API reachability.
- If PowerShell blocks `npm.ps1`, use `npm.cmd run runtime:check` in the same terminal session.
- Result is `ok: true` only when all external runtime checks pass.

## Strict Audit

- Run `JARVIS: AUDIT repo=<name> strict_external=true`.
- With `strict_external=true`, audit requires runtime readiness in addition to quality/document checks.

## Release Safety Audit

- Run `npm run audit:safety` to execute a consolidated release-safety audit.
- If PowerShell blocks `npm.ps1`, use `npm.cmd run audit:safety`.
- The command generates `docs/audits/release_safety_report.json`.
- Release candidate is ready only when report field `ok` is `true`.

## Proposal Intake

- Save the client proposal file in the repository (example: `proposals/cliente_x.md`).
- If the proposal is vague, the pipeline generates guided discovery and pre-kickoff gates automatically.
- Commercial decision thresholds are versioned in `config/decision_policy.json`.
- Run segment calibration with real decision history:
  - `npm run policy:calibrate`
- Start with proposal context:
  - `JARVIS: START project=<name> proposal_file=proposals/cliente_x.md`
- Run execution cycle to produce proposal assessment:
  - `JARVIS: EXEC cycle=1 mode=autopilot_safe`
- Optional one-shot pipeline command:
  - `python scripts/run_pipeline.py --project <name> --cycle 1 --mode autopilot_safe --proposal-file proposals/cliente_x.md --strict-external`
  - with challenger in shadow mode:
    - `python scripts/run_pipeline.py --project <name> --cycle 1 --mode autopilot_safe --proposal-file proposals/cliente_x.md --strict-external --shadow`
- Core output:
  - `docs/26_proposta_avaliacao.md`
  - `docs/27_descoberta_guiada.md`
  - `docs/28_validacao_pre_kickoff.md`
  - `docs/31_politica_decisao_comercial.md`
  - `docs/32_programa_treinamento_agentes.md`
  - `docs/33_scorecard_agentes.md`
  - `docs/audits/proposal_decision_history.jsonl`
  - `docs/audits/decision_policy_calibration_report.json`
  - `docs/audits/agent_score_history.jsonl`
  - `docs/audits/agent_leaderboard.json`
  - `docs/audits/shadow_mode_report.json`

## Stage Validation Policy

- Policy file: `config/stage_validation.json`
- Gate behavior:
  - stage only passes with `stage_validation_ok=true`
  - mandatory `handoff_packet` in every stage output
  - missing contract/notes/artifacts blocks pipeline
- Validate policy and protocol with:
  - `npm run quality:python`

## Agent Leaderboard

- Build leaderboard manually:
  - `npm run agents:leaderboard`
- Config file:
  - `config/agent_training.json`
- Promotion/readiness criteria are evaluated from rolling history.

## Cross-Platform Readiness

- `package.json` scripts are Linux-ready and Windows-ready.
- Quality gate enforces portability through:
  - `checks.npm_scripts_cross_platform = true`

## Client Template Pack

- Standard templates are stored in:
  - `templates/client_packet`
- Generate a packet for each client/proposal:
  - `python scripts/init_client_templates.py --client "<client>" --project "<project>" --owner "<owner>"`
  - `npm run templates:init -- --client "<client>" --project "<project>" --owner "<owner>"`
- Quality gate enforces template availability through:
  - `checks.client_templates_available = true`
