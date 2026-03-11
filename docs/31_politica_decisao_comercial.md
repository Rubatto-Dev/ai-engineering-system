# Politica de Decisao Comercial

## Versao ativa
- version: `1.1.1`
- arquivo de configuracao: `config/decision_policy.json`
- historico de decisoes: `docs/audits/proposal_decision_history.jsonl`
- relatorio de calibracao: `docs/audits/decision_policy_calibration_report.json`

## Objetivo
- Padronizar decisao `GO`, `GO_COM_RESSALVAS` e `NO_GO` antes de iniciar implementacao.
- Reduzir aprovacao subjetiva quando proposta chega vaga ou incompleta.
- Ajustar thresholds por segmento com base em historico real.

## Segmentos calibrados

### Frontend
- `go_min_score`: `0.74`
- `go_with_caveats_min_score`: `0.58`
- `go_max_ambiguity_score`: `0.57`
- `go_max_open_gaps`: `3`
- `no_go_max_score`: `0.46`
- `no_go_min_open_gaps`: `4`
- `no_go_min_ambiguity_score`: `0.75`

### Backend
- `go_min_score`: `0.73`
- `go_with_caveats_min_score`: `0.62`
- `go_max_ambiguity_score`: `0.55`
- `go_max_open_gaps`: `4`
- `no_go_max_score`: `0.48`
- `no_go_min_open_gaps`: `5`
- `no_go_min_ambiguity_score`: `0.75`

### Automacao
- `go_min_score`: `0.67`
- `go_with_caveats_min_score`: `0.58`
- `go_max_ambiguity_score`: `0.63`
- `go_max_open_gaps`: `4`
- `no_go_max_score`: `0.44`
- `no_go_min_open_gaps`: `5`
- `no_go_min_ambiguity_score`: `0.75`

### Fullstack
- `go_min_score`: `0.71`
- `go_with_caveats_min_score`: `0.61`
- `go_max_ambiguity_score`: `0.59`
- `go_max_open_gaps`: `4`
- `no_go_max_score`: `0.47`
- `no_go_min_open_gaps`: `5`
- `no_go_min_ambiguity_score`: `0.72`

## Regra pratica
- `GO`: score acima do limite do segmento e risco controlado.
- `GO_COM_RESSALVAS`: score viavel, mas com ambiguidade/gaps acima do limite de `GO`.
- `NO_GO`: score baixo para o nivel de risco atual ou combinacao critica de gaps e ambiguidade.

## Operacao
- Executar calibracao:
  - `npm run policy:calibrate`
- O comando:
  - atualiza `config/decision_policy.json` quando houver dados suficientes
  - registra `last_calibrated_at` na policy
  - gera relatorio em `docs/audits/decision_policy_calibration_report.json`

## Controles de estabilidade da calibracao
- `calibration.window_days`: considera apenas historico recente.
- `calibration.min_score_spread`: bloqueia ajuste com score quase sem variacao.
- `calibration.min_ambiguity_spread`: bloqueia ajuste com ambiguidade quase sem variacao.
- Se os controles falharem, a calibracao preserva os thresholds atuais do segmento.

## Governanca
- Qualquer mudanca de thresholds exige:
  - atualizar `config/decision_policy.json`
  - registrar nova versao nesta documentacao
  - validar com `npm run test:python`, `npm run quality:python` e `npm run audit:safety`
