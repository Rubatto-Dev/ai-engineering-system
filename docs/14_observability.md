# Observability

## Sinais operacionais obrigatorios

- Logs estruturados por etapa e agente.
- Correlacao de trace por ciclo (`project`, `cycle`, `agent_id`).
- Latencia por etapa do pipeline.
- Saude dos gates de qualidade e runtime.

## Comandos de monitoramento

- `npm run test:python`
- `npm run quality:python`
- `npm run runtime:check`
- `npm run audit:safety`

## Indicadores monitorados no pos-merge

- `tests_ok`
- `quality_ok`
- `runtime_ok`
- `strict_audit_ok`
- `sonar_api_reachable`

## Regra de alerta

Se qualquer indicador acima ficar `false`, classificar incidente como operacional e bloquear novo `SHIP` ate revalidacao completa dos quatro comandos.
