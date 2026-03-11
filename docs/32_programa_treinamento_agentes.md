# Programa de Treinamento dos Agentes

## Objetivo

Treinar e selecionar um time de agentes capaz de transformar propostas vagas de clientes em documentacao profissional completa, com bloqueio automatico de qualquer etapa nao validada.

## Principios operacionais

- Zero falha silenciosa: qualquer inconsistencia bloqueia a etapa.
- Comunicacao estruturada: todo agente publica `handoff_packet`.
- Rastreabilidade ponta a ponta: toda decisao deve apontar evidencia.
- Melhoria continua: scorecard semanal e recalibracao de policy.

## Trilha de treinamento

### Fase T1 - Dataset Ouro
- Coletar propostas reais anonimizadas (`frontend`, `backend`, `automacao`, `fullstack`).
- Rotular saida esperada:
  - requisitos
  - escopo
  - stack
  - riscos
  - estimativa
  - decisao (`GO`, `GO_COM_RESSALVAS`, `NO_GO`)
- Meta inicial: 30 casos; meta operacional: 100+ casos.

### Fase T2 - Torneio de configuracoes
- Rodar variantes de prompt/modelo com o mesmo dataset.
- Avaliar por scorecard padrao (documento `docs/33_scorecard_agentes.md`).
- Promover apenas variantes acima do threshold de producao.

### Fase T3 - Shadow mode
- Executar agente campeao em paralelo ao fluxo oficial.
- Comparar diferencas de decisao e cobertura de documentacao.
- Liberar para producao somente apos estabilidade em 3 ciclos.

### Fase T4 - Calibracao continua
- Atualizar thresholds comerciais com `npm run policy:calibrate`.
- Revisar drift por segmento com janela temporal configurada.
- Rebaixar variante quando cair abaixo do score minimo.

## Regras de comunicacao sem brecha

- Toda etapa deve publicar `handoff_packet` com:
  - `summary`
  - `assumptions`
  - `risks`
  - `open_questions`
  - `validation_snapshot`
- Sem `handoff_packet_ok=true`, pipeline nao avanca.
- Sem `stage_validation_ok=true`, pipeline nao avanca.

## Cadencia recomendada

- Diario: revisar falhas de stage validation e corrigir raiz.
- Semanal: atualizar leaderboard de agentes.
- Quinzenal: revisar dataset ouro e incluir novos casos reais.
- Mensal: revisao executiva de acuracia de decisao e retrabalho.
