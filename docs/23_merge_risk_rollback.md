# Merge Risk and Rollback - Fase 2

## Objetivo

Definir criterios de risco e plano de rollback para merge seguro da branch de consolidacao da Fase 2.

## Gates obrigatorios pre-merge

- `npm run test:python` -> deve passar.
- `npm run quality:python` -> deve retornar `ok: true`.
- `npm run runtime:check` -> deve retornar `ok: true`.
- `npm run audit:safety` -> deve retornar `ok: true`.
- `docs/audits/release_safety_report.json` atualizado e anexado no PR.

## Matriz de risco de merge

### Risco 1 - Regressao de contrato de handoff
- Impacto: alto
- Sinal: falhas em `test_pipeline_integration` ou `test_agents`
- Mitigacao: bloquear merge ate suite verde; revisar `BaseAgent.enforce_contract`

### Risco 2 - Runtime externo instavel
- Impacto: alto
- Sinal: `runtime:check` com `sonar_api_reachable=false`
- Mitigacao: manter Docker/Sonar ativos e repetir `audit:safety`

### Risco 3 - Divergencia documental vs. implementacao
- Impacto: medio
- Sinal: checklist do PR incompleto ou evidencias desatualizadas
- Mitigacao: validar `docs/11_validacao.md`, `docs/21_fase2_changelog.md` e report JSON

## Plano de rollback pos-merge

### Cenário A - Falha critica imediata apos merge
1. Identificar commit de merge no `main`.
2. Reverter commit de merge:
   - `git revert -m 1 <merge_commit_sha>`
3. Executar novamente:
   - `npm run test:python`
   - `npm run quality:python`
   - `npm run runtime:check`

### Cenário B - Falha operacional sem regressao de codigo
1. Reexecutar `npm run sonar:up`.
2. Reexecutar `npm run runtime:check`.
3. Reexecutar `npm run audit:safety`.
4. Se normalizar, manter merge e registrar incidente.

## Responsabilidade de aprovacao

- Reviewer tecnico: valida codigo, testes e contratos.
- Reviewer operacional: valida runtime/auditoria.
- Merge owner: executa checklist final e aprova merge apenas com todos os gates verdes.
