# Release Safety Checklist

## Objetivo

Padronizar a auditoria de seguranca de release com evidencias reprodutiveis antes de `SHIP`.

## Checklist obrigatorio

- `tests_ok`: suite Python sem falhas.
- `quality_ok`: quality gate interno com docs, ADR, seguranca e tooling em conformidade.
- `runtime_ok`: runtime externo pronto (Node/npm/MCPs/SonarQube API).
- `strict_audit_ok`: `JARVIS: AUDIT ... strict_external=true` em status `audit_ok`.

## Execucao recomendada

1. Garantir SonarQube local ativo (`npm run sonar:up`).
2. Rodar auditoria completa:
   - `npm run audit:safety`
3. Confirmar no JSON:
   - `ok: true`
   - todos os checks em `true`

## Evidencia gerada

- Arquivo: `docs/audits/release_safety_report.json`
- Conteudo:
  - resumo de checks
  - detalhes de testes, quality, runtime e strict audit
  - timestamp UTC da execucao

## Criterio de bloqueio

Se qualquer check estiver `false`, release deve permanecer bloqueado ate nova execucao com `ok: true`.
