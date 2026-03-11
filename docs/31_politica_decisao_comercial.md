# Politica de Decisao Comercial

## Versao ativa
- version: `1.0.0`
- arquivo de configuracao: `config/decision_policy.json`

## Objetivo
- Padronizar decisao `GO`, `GO_COM_RESSALVAS` e `NO_GO` antes de iniciar implementacao.
- Reduzir aprovacao subjetiva quando proposta chega vaga ou incompleta.

## Thresholds (v1.0.0)
- `go_min_score`: `0.78`
- `go_with_caveats_min_score`: `0.52`
- `go_max_ambiguity_score`: `0.45`
- `go_max_open_gaps`: `2`
- `no_go_max_score`: `0.40`
- `no_go_min_open_gaps`: `7`
- `no_go_min_ambiguity_score`: `0.88`

## Regras praticas
- `GO`: score alto, ambiguidade baixa e poucos gaps abertos.
- `GO_COM_RESSALVAS`: proposta viavel com discovery pendente (gaps/ambiguidade acima do limite de `GO`).
- `NO_GO`: risco elevado com score baixo ou combinacao critica de gaps + ambiguidade.

## Governanca
- Qualquer mudanca de thresholds exige:
  - atualizar `config/decision_policy.json`
  - registrar nova versao nesta documentacao
  - validar com `npm run test:python` e `npm run audit:safety`
