# AI Engineering System

Sistema de engenharia assistida por IA orientado por agentes, com protocolo Jarvis, memoria global, quality gate e validacao por testes em 3 camadas.

## Stack inicial

- Python 3.10+
- Pytest (unit, integration, e2e)
- SonarQube (quality gate externo, via integracao)
- Context7 e Sequential Thinking (fontes de contexto e raciocinio estruturado)

## Comandos Jarvis

- `JARVIS: START project=<name>`
- `JARVIS: PLAN cycle=<n>`
- `JARVIS: EXEC cycle=<n> mode=autopilot_safe`
- `JARVIS: AUDIT repo=<name>`
- `JARVIS: SHIP version=<semver>`

## Checks operacionais rapidos

- `npm run test:python`
- `npm run quality:python`
- `scripts\run_runtime_check.cmd`
- `JARVIS: AUDIT repo=<name> strict_external=true`
- `npm run sonar:up` (inicia SonarQube local em `http://localhost:9000`)
- `npm run sonar:down`
