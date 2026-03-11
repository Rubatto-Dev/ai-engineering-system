# PR Review Checklist - Fase 2

## Objetivo

Padronizar a revisao tecnica do PR de consolidacao da Fase 2, garantindo merge seguro e rastreavel.

## Escopo do PR

- Fechamento documental da Fase 1.
- Hardening da Fase 2 em runtime, contratos tipados e auditoria estrita.
- Pacote de release safety com comando unico e evidencia JSON.

## Checklist de revisao tecnica

- [ ] Mudancas de codigo tem cobertura de teste adequada.
- [ ] Failure-modes novos estao cobertos por unit ou integration tests.
- [ ] Contratos de handoff continuam consistentes no pipeline.
- [ ] Runtime check permanece estavel com SonarQube ativo.
- [ ] Nao ha regressao no fluxo `START -> PLAN -> EXEC -> AUDIT -> SHIP`.

## Checklist de qualidade operacional

- [ ] `npm run test:python` sem falhas.
- [ ] `npm run quality:python` com `ok: true`.
- [ ] `npm run runtime:check` com `ok: true`.
- [ ] `npm run audit:safety` com `ok: true`.
- [ ] `docs/audits/release_safety_report.json` atualizado no PR.

## Checklist de documentacao

- [ ] `docs/10_backlog.md` reflete etapas concluídas.
- [ ] `docs/11_validacao.md` registra evidencias por etapa.
- [ ] `docs/20_release_safety_checklist.md` esta consistente com os scripts.
- [ ] `docs/21_fase2_changelog.md` descreve escopo e criterios de aceite.

## Criterio de merge

Merge permitido apenas com todos os checklists aprovados e sem bloqueios abertos.

## Template de comentario final no PR

```md
## Review Outcome
- Status: approved | changes_requested
- Scope verified: yes/no
- Tests and gates: pass/fail
- Runtime and strict audit: pass/fail
- Residual risks: <list or none>
- Merge recommendation: merge/block
```
