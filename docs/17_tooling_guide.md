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

- Run `scripts\run_runtime_check.cmd` to validate Node, npm, MCP runtime startup, and SonarQube API reachability.
- Result is `ok: true` only when all external runtime checks pass.

## Strict Audit

- Run `JARVIS: AUDIT repo=<name> strict_external=true`.
- With `strict_external=true`, audit requires runtime readiness in addition to quality/document checks.

## Release Safety Audit

- Run `npm run audit:safety` to execute a consolidated release-safety audit.
- The command generates `docs/audits/release_safety_report.json`.
- Release candidate is ready only when report field `ok` is `true`.

## Proposal Intake

- Save the client proposal file in the repository (example: `proposals/cliente_x.md`).
- Start with proposal context:
  - `JARVIS: START project=<name> proposal_file=proposals/cliente_x.md`
- Run execution cycle to produce proposal assessment:
  - `JARVIS: EXEC cycle=1 mode=autopilot_safe`
- Core output:
  - `docs/26_proposta_avaliacao.md`
