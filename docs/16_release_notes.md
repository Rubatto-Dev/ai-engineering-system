# 16_release_notes.md

Gerado e atualizado automaticamente pelo pipeline.

## Release 0.2.0 - 2026-03-06
- Ship gate passed
- SonarQube: ok
- Security checks: ok

## Release 0.3.0 - 2026-03-11
- Fase 1 consolidada e encerrada
- Fase 2 hardening consolidada (runtime, contratos, auditoria estrita)
- Release safety audit com `ok: true`
- PR de consolidacao integrado no `main`
- Monitoramento pos-merge concluido sem incidentes

## Release 0.3.1 - 2026-03-11
- Fluxo de proposta de cliente integrado ao `START/EXEC`
- Avaliacao automatizada de valor, viabilidade, duracao e stack recomendada
- Geracao de documentacao base para tomada de decisao pre-execucao
- Suite de testes expandida para cobrir cenario de proposta (34 testes)

## Release 0.3.2 - 2026-03-11
- Roadmap do PM calibrado por proposta com timeline estimada em `docs/12_roadmap.md`
- Runner operacional `scripts/run_pipeline.py` com `--proposal-file` e `--strict-external`
- Validacao piloto ponta a ponta para proposta de cliente (decisao `GO_COM_RESSALVAS`)
- Suite de testes expandida para 35 testes

## Release 0.3.3 - 2026-03-11
- Tratamento robusto de proposta vaga com score de ambiguidade e recomendacao de kickoff
- Novo pacote de discovery e gate:
  - `docs/27_descoberta_guiada.md`
  - `docs/28_validacao_pre_kickoff.md`
- Backlog dinamico prioriza discovery quando gaps criticos estao abertos
- Suite de testes expandida para 37 testes

## Release 0.3.4 - 2026-03-11
- Thresholds comerciais versionados para decisao (`GO`, `GO_COM_RESSALVAS`, `NO_GO`)
- Policy engine integrada ao `IdeaValidator`
- Configuracao em `config/decision_policy.json` validada pelo quality gate
- Documentacao de governanca adicionada em `docs/31_politica_decisao_comercial.md`
- Suite de testes expandida para 41 testes

## Release 0.3.5 - 2026-03-11
- Calibracao de thresholds por segmento (`frontend`, `backend`, `automacao`, `fullstack`) com historico real
- Historico de decisao operacional em `docs/audits/proposal_decision_history.jsonl`
- Relatorio de calibracao em `docs/audits/decision_policy_calibration_report.json`
- Comando operacional novo: `npm run policy:calibrate`
- Suite de testes expandida para 45 testes
