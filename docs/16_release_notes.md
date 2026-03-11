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
