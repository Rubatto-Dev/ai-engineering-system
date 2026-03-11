# Validacao

## Baseline anterior

- ok: true
- missing: 0
- empty: 0

## Fase 1 - ciclo de retomada (2026-03-11)

### Evidencias executadas

- `npm run test:python` -> `19 passed`
- `npm run quality:python` -> `ok: true`
- `npm run runtime:check` -> `ok: true`
- Runtime externo validado:
  - `sonar_api_reachable: true`
  - endpoint: `http://localhost:9000/api/system/status`
  - resposta Sonar: `status=UP` e `status_code=200`

### Incidente resolvido no ciclo

- Falha inicial observada:
  - `npm run runtime:check` com `RemoteDisconnected` durante bootstrap do SonarQube
- Mitigacao aplicada:
  - tratamento defensivo de excecao transiente HTTP no probe de Sonar em `src/ai_engineering_os/external_runtime.py`
  - novo teste unitario de regressao em `tests/unit/test_external_runtime.py`
  - Docker Desktop ativo e `npm run sonar:up` executado com sucesso
- Resultado final:
  - runtime check estabilizado e sem crash
  - bloqueio operacional encerrado

## Sequential Thinking Trace

1. Ler handoff e identificar proximo ciclo declarado
2. Priorizar backlog da Fase 1 por risco e dependencia
3. Executar checks tecnicos obrigatorios do ciclo e corrigir falha transiente
4. Reexecutar runtime check e fechar bloqueio externo

## Project Extractor Snapshot

- python_files: 28
- api_contracts: docs/07_api.md
- data_model: docs/06_modelo_dados.md
- dependencies: pyproject.toml and package.json

## Refactor Recommendations

- Centralizar helpers de escrita para reduzir duplicacao de orquestracao
- Manter saidas dos agentes estritamente tipadas
- Expandir testes de failure-mode em cada handoff de etapa

## Fase 2 - Microetapas executadas (2026-03-11)

### Etapa 1 - Failure-mode de runtime (agregador)

- Mudanca:
  - novos testes unitarios para `evaluate_runtime_readiness` em `tests/unit/test_runtime_readiness.py`
- Cobertura adicionada:
  - falha quando Sonar esta indisponivel
  - sucesso quando todas as probes estao prontas
- Validacao da etapa:
  - `npm run test:python` -> `21 passed`
  - `npm run quality:python` -> `ok: true`

### Etapa 2 - Contratos tipados no handoff de agentes

- Mudanca:
  - validacao de shape de `AgentResult` em `BaseAgent.enforce_contract`
  - checks adicionados: `result_schema_ok` e `result_schema_errors`
- Cobertura adicionada:
  - erro por `handoff` em formato invalido
  - erro por `agent_id` divergente do agente executor
  - assert de schema no teste de integracao do pipeline
- Validacao da etapa:
  - `npm run test:python` -> `23 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm run runtime:check` -> `ok: true`

### Etapa 3 - Failure-mode de handoff no pipeline

- Mudanca:
  - novo teste de integracao em `tests/integration/test_pipeline_integration.py`
- Cobertura adicionada:
  - pipeline para quando um agente viola handoff esperado por contrato
  - valida `failed_agent`, `reason` e trace final com `contract_handoff_match=false`
- Validacao da etapa:
  - `npm run test:python` -> `24 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm run runtime:check` -> `ok: true`

### Etapa 4 - Auditoria estrita e seguranca de ship

- Mudanca:
  - novos testes unitarios em `tests/unit/test_jarvis_audit.py`
- Cobertura adicionada:
  - sucesso de `AUDIT strict_external=true` quando runtime externo esta pronto
  - bloqueio de `SHIP` apos `AUDIT` estrita com falha
- Validacao da etapa:
  - `npm run test:python` -> `26 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm run runtime:check` -> `ok: true`

### Etapa 5 - Pacote de auditoria para release safety

- Mudanca:
  - modulo `src/ai_engineering_os/release_safety.py`
  - script `scripts/release_safety_audit.py`
  - comando `npm run audit:safety`
  - checklist em `docs/20_release_safety_checklist.md`
- Cobertura adicionada:
  - testes unitarios do agregador em `tests/unit/test_release_safety.py`
- Evidencia gerada:
  - `docs/audits/release_safety_report.json` com `ok: true`
- Validacao da etapa:
  - `npm run test:python` -> `28 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm run runtime:check` -> `ok: true`
  - `npm run audit:safety` -> `ok: true`

### Etapa 6 - Consolidacao de aceite da Fase 2

- Mudanca:
  - novo changelog tecnico em `docs/21_fase2_changelog.md`
- Cobertura adicionada:
  - criterios de aceite explicitos por comando
  - riscos residuais e acao recomendada para PR interno
- Validacao da etapa:
  - evidencias da etapa 5 reutilizadas (sem alteracao de codigo)

### Etapa 7 - PR interno de consolidacao

- Mudanca:
  - branch criada: `feat/fase2-release-safety-hardening`
  - commit de consolidacao publicado no remoto
- Evidencia:
  - commit: `a8f9439`
  - branch remota: `origin/feat/fase2-release-safety-hardening`
- Validacao da etapa:
  - PR aberto manualmente no GitHub pelo responsavel

### Etapa 8 - Checklist de revisao do PR

- Mudanca:
  - novo documento `docs/22_pr_review_checklist.md`
- Cobertura adicionada:
  - checklist tecnico, operacional, documental e criterio de merge
  - template de comentario final de review
- Validacao da etapa:
  - validacao tecnica reexecutada apos atualizacao documental

### Etapa 9 - Plano de risco e rollback de merge

- Mudanca:
  - novo documento `docs/23_merge_risk_rollback.md`
- Cobertura adicionada:
  - gates obrigatorios pre-merge
  - matriz de risco de merge
  - procedimento de rollback pos-merge
- Validacao da etapa:
  - validacao tecnica reexecutada apos atualizacao documental

### Etapa 10 - Recomendacao final de merge

- Mudanca:
  - novo documento `docs/24_pr_merge_recommendation.md`
- Cobertura adicionada:
  - decisao `approved` com gates e condicao de merge
- Validacao da etapa:
  - `npm run test:python` -> `28 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm run runtime:check` -> `ok: true`
  - `npm run audit:safety` -> `ok: true`

### Etapa 11 - Merge no main e release final

- Mudanca:
  - branch `main` atualizada com merge da consolidacao da Fase 2
  - release notes atualizados em `docs/16_release_notes.md` (Release 0.3.0)
- Validacao da etapa:
  - `npm run test:python` -> `28 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm run runtime:check` -> `ok: true`
  - `npm run audit:safety` -> `ok: true`

### Etapa 12 - Monitoramento pos-merge e encerramento operacional

- Mudanca:
  - observabilidade operacional detalhada em `docs/14_observability.md`
  - fechamento operacional registrado em `docs/25_post_merge_operational_closure.md`
- Cobertura adicionada:
  - sinais operacionais e regra de alerta para bloqueio de ship
  - evidencias de estabilidade pos-merge no `main`
- Validacao da etapa:
  - `npm run test:python` -> `28 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm run runtime:check` -> `ok: true`
  - `npm run audit:safety` -> `ok: true`

### Etapa 13 - Time de agentes para proposta de cliente

- Mudanca:
  - novo modulo `src/ai_engineering_os/proposal_profile.py`
  - `JARVIS: START` com suporte a `proposal_file=<path>`
  - pipeline com `proposal_profile` propagado para agentes
  - agentes reforcados para gerar docs orientados a valor/viabilidade/tempo/stack/riscos
- Cobertura adicionada:
  - `tests/unit/test_proposal_profile.py`
  - `tests/unit/test_jarvis_proposal.py`
  - `tests/integration/test_pipeline_integration.py` (cenario com proposta)
- Documentacao adicionada:
  - `docs/30_template_proposta_cliente.md`
  - `README.md` com fluxo de proposta de cliente
- Validacao da etapa:
  - `npm run test:python` -> `34 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm run runtime:check` -> `ok: true`
  - `npm run audit:safety` -> `ok: true`

### Etapa 14 - Validacao de proposta piloto e calibracao de roadmap

- Mudanca:
  - `src/ai_engineering_os/agents/pm.py` passou a usar `proposal_profile` para milestone inicial de discovery e timeline no roadmap.
  - `tests/unit/test_agents.py` ganhou cobertura para comportamento de roadmap orientado por proposta.
  - `scripts/run_pipeline.py` passou a aceitar `--proposal-file` e `--strict-external` para execucao operacional do fluxo de proposta.
- Validacao de ponta a ponta (workspace temporario):
  - proposta piloto com objetivo, features, prazo, budget, KPI e requisito de seguranca.
  - `START` com proposta carregada: `proposal_loaded=true`.
  - perfil inferido:
    - `project_type: fullstack`
    - `feasibility: media`
    - `estimated_duration_weeks: 9-16 (avg 12)`
    - `value_score: 0.71`
  - artefatos confirmados:
    - `docs/26_proposta_avaliacao.md`
    - `docs/12_roadmap.md` com `## Timeline`.
  - decisao gerada: `GO_COM_RESSALVAS`.
- Validacao da etapa:
  - `npm run test:python` -> `35 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm.cmd run runtime:check` -> `ok: true`
  - `npm.cmd run audit:safety` -> `ok: true`

### Etapa 15 - Propostas vagas com discovery guiada e gate pre-kickoff

- Mudanca:
  - `src/ai_engineering_os/proposal_profile.py` reforcado com:
    - `ambiguity_score` e `ambiguity_level`
    - `discovery_questions` e `validation_checklist`
    - `kickoff_recommendation` e `scope_lock_ready`
  - `src/ai_engineering_os/agents/intake.py` agora gera `docs/27_descoberta_guiada.md`.
  - `src/ai_engineering_os/agents/documentation_qa.py` agora gera `docs/28_validacao_pre_kickoff.md`.
  - `src/ai_engineering_os/agents/idea_validator.py` e `backlog.py` ajustados para proposta vaga.
  - `src/ai_engineering_os/repository.py` atualizado para incluir docs 27/28 como documentacao base.
- Cobertura adicionada:
  - `tests/unit/test_proposal_profile.py` (cenario de proposta vaga)
  - `tests/integration/test_pipeline_integration.py` (geracao de docs 27/28 e `kickoff_ready=false`)
- Validacao da etapa:
  - `npm run test:python` -> `37 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm.cmd run runtime:check` -> `ok: true`
  - `npm.cmd run audit:safety` -> `ok: true`

### Etapa 16 - Thresholds comerciais versionados (GO/GO_COM_RESSALVAS/NO_GO)

- Mudanca:
  - novo modulo `src/ai_engineering_os/decision_policy.py` para carregar/aplicar politica comercial.
  - nova configuracao versionada em `config/decision_policy.json`.
  - `IdeaValidator` passou a aplicar policy comercial (decisao base por score + ajuste por ambiguidade/gaps/viabilidade).
  - quality gate reforcado para validar `decision_policy_configured=true`.
- Documentacao adicionada:
  - `docs/31_politica_decisao_comercial.md`
- Cobertura adicionada:
  - `tests/unit/test_decision_policy.py`
  - `tests/unit/test_quality_gate.py` (falha quando decision policy esta ausente)
- Validacao da etapa:
  - `npm run test:python` -> `41 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm.cmd run runtime:check` -> `ok: true`
  - `npm.cmd run audit:safety` -> `ok: true`

### Etapa 17 - Calibracao de thresholds por segmento com historico real

- Mudanca:
  - novo modulo `src/ai_engineering_os/decision_calibration.py`.
  - novo comando operacional: `npm run policy:calibrate`.
  - `IdeaValidator` agora registra historico em `docs/audits/proposal_decision_history.jsonl`.
  - policy ampliada para `segment_thresholds` em `config/decision_policy.json`.
  - quality gate reforcado para validar schema segmentado da policy.
- Dados usados na calibracao:
  - historico consolidado: `23` decisoes
  - segmentos com amostra valida:
    - frontend: `5`
    - backend: `5`
    - automacao: `5`
    - fullstack: `8`
  - relatorio: `docs/audits/decision_policy_calibration_report.json`
- Resultado:
  - policy atualizada para versao `1.1.1`.
  - `last_calibrated_at` preenchido em `config/decision_policy.json`.
- Cobertura adicionada:
  - `tests/unit/test_decision_calibration.py`
  - `tests/unit/test_decision_policy.py` (segment thresholds)
  - `tests/unit/test_quality_gate.py` (schema segmentado da policy)
- Validacao da etapa:
  - `npm run test:python` -> `45 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm.cmd run runtime:check` -> `ok: true`
  - `npm.cmd run audit:safety` -> `ok: true`

### Etapa 18 - Calibracao temporal com regra de estabilidade

- Mudanca:
  - `src/ai_engineering_os/decision_calibration.py` reforcado com:
    - `window_days` para calibrar apenas historico recente.
    - `min_score_spread` e `min_ambiguity_spread` para evitar ajuste com baixa variancia.
  - `src/ai_engineering_os/decision_policy.py`, `repository.py` e `quality_gate.py` atualizados para novas chaves de calibracao.
  - `config/decision_policy.json` atualizado com os novos parametros.
- Cobertura adicionada:
  - `tests/unit/test_decision_calibration.py`
    - ignora historico fora da janela
    - bloqueia calibracao por variancia insuficiente
- Validacao da etapa:
  - `npm run test:python` -> `47 passed`
  - `npm run quality:python` -> `ok: true`
  - `npm.cmd run runtime:check` -> `ok: true`
  - `npm.cmd run audit:safety` -> `ok: true`

### Etapa 19 - Stage validation bloqueante e comunicacao sem brecha

- Mudanca:
  - `BaseAgent.enforce_contract` agora exige:
    - `handoff_packet` obrigatorio em `outputs`
    - checklist `stage_validation_ok` com bloqueio automatico quando houver falha
  - `quality_gate` reforcado com:
    - `stage_validation_policy_configured`
    - `communication_protocol_configured`
  - nova policy: `config/stage_validation.json`
  - protocolos atualizados:
    - `protocol/AGENT_COMMUNICATION_PROTOCOL.md`
    - `protocol/VALIDATION_RULES.md`
  - programa de treino formalizado:
    - `docs/32_programa_treinamento_agentes.md`
    - `docs/33_scorecard_agentes.md`
- Cobertura adicionada:
  - `tests/unit/test_agents.py` (handoff packet + bloqueio por notes ausentes)
  - `tests/unit/test_quality_gate.py` (falha sem policy de stage validation e sem protocolo)
  - `tests/integration/test_pipeline_integration.py` (assert de `stage_validation_ok` e `handoff_packet_ok`)
- Validacao da etapa:
  - `npm run test:python` -> `51 passed`
  - `npm run quality:python` -> `ok: true`
