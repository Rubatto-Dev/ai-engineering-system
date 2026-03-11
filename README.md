# AI Engineering System

Sistema de engenharia assistida por IA orientado por agentes, com protocolo Jarvis, memoria global, quality gate e validacao por testes em 3 camadas.

## Stack inicial

- Python 3.10+
- Pytest (unit, integration, e2e)
- SonarQube (quality gate externo, via integracao)
- Context7 e Sequential Thinking (fontes de contexto e raciocinio estruturado)

## Comandos Jarvis

- `JARVIS: START project=<name>`
- `JARVIS: START project=<name> proposal_file=<relative_path>`
- `JARVIS: PLAN cycle=<n>`
- `JARVIS: EXEC cycle=<n> mode=autopilot_safe`
- `JARVIS: AUDIT repo=<name>`
- `JARVIS: SHIP version=<semver>`

## Fluxo de proposta de cliente

1. Salvar a proposta em arquivo de texto/markdown no repositorio, por exemplo:
   - `proposals/cliente_acme.md`
2. Iniciar o projeto com a proposta:
   - `JARVIS: START project=acme proposal_file=proposals/cliente_acme.md`
3. Planejar e executar:
   - `JARVIS: PLAN cycle=1`
   - `JARVIS: EXEC cycle=1 mode=autopilot_safe`
   - opcional (one-shot): `python scripts/run_pipeline.py --project acme --cycle 1 --mode autopilot_safe --proposal-file proposals/cliente_acme.md --strict-external`
4. Validar:
   - `npm run test:python`
   - `npm run quality:python`
   - `npm run runtime:check`
   - `npm run audit:safety`

Saidas principais geradas para avaliacao inicial:
- `docs/26_proposta_avaliacao.md` (valor, viabilidade, estimativa, stack, riscos e gaps)
- `docs/01_visao.md`, `docs/02_requisitos.md`, `docs/05_arquitetura.md`, `docs/10_backlog.md`

## Checks operacionais rapidos

- `npm run test:python`
- `npm run quality:python`
- `scripts\run_runtime_check.cmd`
- `JARVIS: AUDIT repo=<name> strict_external=true`
- `npm run sonar:up` (inicia SonarQube local em `http://localhost:9000`)
- `npm run sonar:down`
