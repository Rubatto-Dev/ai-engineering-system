# Scorecard de Elite dos Agentes

## Objetivo

Definir criterios objetivos para selecionar e manter apenas os melhores agentes em producao.

## Criterios e pesos

| Criterio | Peso | Regra |
|---|---:|---|
| Cobertura de requisitos | 25% | Percentual de requisitos obrigatorios cobertos na saida |
| Qualidade de estimativa | 20% | Erro medio entre estimado e realizado |
| Qualidade de decisao comercial | 20% | Acerto entre decisao prevista e resultado real |
| Comunicacao de handoff | 20% | `handoff_packet` completo e sem campos faltantes |
| Conformidade de validacao | 15% | `stage_validation_ok=true` em todas as etapas |

## Thresholds de producao

- Score global minimo: `0.90`
- Cobertura de requisitos minima: `0.95`
- Erro medio de estimativa maximo: `0.20`
- Violacao de handoff por ciclo: `0`
- Etapas sem validacao completa: `0`

## Formula

`score_global = sum(peso_i * score_i)`

Cada `score_i` deve ser normalizado em faixa `0.0-1.0`.

## Regras de promocao e rebaixamento

- Promocao: 3 ciclos consecutivos com score >= 0.90.
- Observacao: score entre 0.85 e 0.89 por 2 ciclos.
- Rebaixamento: score < 0.85 em qualquer ciclo critico.

## Evidencias obrigatorias por ciclo

- Relatorio de decisao: `docs/26_proposta_avaliacao.md`
- Gate pre-kickoff: `docs/28_validacao_pre_kickoff.md`
- Historico de decisoes: `docs/audits/proposal_decision_history.jsonl`
- Relatorio de calibracao: `docs/audits/decision_policy_calibration_report.json`
- Resultado de gate: `npm run quality:python`
