# Codex Handoff - Plano dos Agentes

## Estado atual

- Repositorio publicado: `https://github.com/Rubatto-Dev/ai-engineering-system`
- Branch remota ativa: `main`
- MCPs configurados no projeto:
  - `context7`
  - `sequential-thinking`
  - `github`
- SonarQube local ativo via Docker Desktop.
- Runtime check validado com `ok: true` em 2026-03-11.

## O que ja foi ajustado

- Git inicializado no projeto `ai-engineering-system`.
- Commit inicial realizado e enviado para o GitHub.
- `config/mcp-servers.json` atualizado com servidor `github`.
- `package.json` atualizado com script `mcp:github`.
- `docs/17_tooling_guide.md` atualizado com instrucoes de GitHub MCP.
- `.gitignore` atualizado para proteger `.env` e ignorar `node_modules`.
- `.env.example` criado com `GITHUB_PERSONAL_ACCESS_TOKEN=`.

## Proximo ciclo (implementacao do plano de agentes)

1. Definir backlog da Fase 1 (escopo minimo de entrega).
2. Priorizar tarefas por risco tecnico e dependencia.
3. Implementar em ciclos curtos com validacao:
   - testes Python (`npm run test:python`)
   - quality checks (`npm run quality:python`)
   - runtime (`npm run runtime:check`)
4. Registrar decisoes tecnicas e atualizacoes de docs a cada ciclo.

## Retomada executada em 2026-03-11

1. Backlog da Fase 1 definido e priorizado em `docs/10_backlog.md`.
2. Roadmap atualizado com fases e marcos em `docs/12_roadmap.md`.
3. Validacao executada:
   - `npm run test:python` -> `19 passed`
   - `npm run quality:python` -> `ok: true`
   - `npm run runtime:check` -> `ok: true`
4. Estabilizacao aplicada:
   - tratamento defensivo de excecao transiente no probe Sonar (`external_runtime.py`)
   - teste de regressao adicionado em `tests/unit/test_external_runtime.py`

## Status da Fase 1

- Status geral: `completed`
- Entregas concluidas:
  - planejamento e priorizacao do backlog
  - atualizacao de roadmap e validacao
  - fechamento de requisitos, arquitetura, API e modelo de dados
  - validacao operacional completa (testes, quality e runtime)

## Proximo ciclo recomendado (Fase 2)

1. Cobrir failure-modes por etapa de handoff.
2. Reforcar contratos tipados entre agentes.
3. Preparar auditoria completa para release candidato.

## Fechamento consolidado em 2026-03-11

- Fase 2 consolidada no `main`.
- Gates tecnicos validados no `main`:
  - `test:python`, `quality:python`, `runtime:check`, `audit:safety`
- Monitoramento pos-merge concluido sem incidentes.
- Proximo ciclo recomendado: iniciar Fase 3 (auditoria final e release candidato).

## Atualizacao Fase 3 (2026-03-11)

- Fluxo de proposta de cliente habilitado:
  - `JARVIS: START project=<name> proposal_file=<path>`
- Time de agentes agora gera avaliacao inicial com:
  - valor estimado
  - viabilidade
  - duracao media
  - stack recomendada
  - riscos e informacoes pendentes
- Novos artefatos de suporte:
  - `docs/26_proposta_avaliacao.md`
  - `docs/30_template_proposta_cliente.md`
  - `proposals/cliente_piloto.md`

## Atualizacao Fase 3 - Etapa 14 (2026-03-11)

- Validacao ponta a ponta executada com proposta piloto em workspace isolado.
- Resultado da proposta piloto:
  - decisao: `GO_COM_RESSALVAS`
  - tipo inferido: `hibrido`
  - viabilidade: `media`
  - duracao estimada: `9-16` semanas (media `12`)
  - valor estimado: `0.71`
- Ajustes de produto concluídos:
  - `ProjectManagerAgent` agora escreve timeline de roadmap a partir do `proposal_profile`.
  - `scripts/run_pipeline.py` suporta `--proposal-file` e `--strict-external`.
  - cobertura unitária adicionada para roadmap orientado por proposta.
- Gates tecnicos revalidados:
  - `test:python` -> `35 passed`
  - `quality:python` -> `ok: true`
  - `runtime:check` -> `ok: true`
  - `audit:safety` -> `ok: true`
- Proxima etapa recomendada:
  - formalizar criterios comerciais de decisao (`GO`, `GO_COM_RESSALVAS`, `NO_GO`) com thresholds versionados.

## Atualizacao Fase 3 - Etapa 15 (2026-03-11)

- Objetivo da etapa:
  - tratar melhor propostas vagas de cliente para ainda assim produzir documentacao profissional completa.
- Entregas:
  - perfil de proposta com nivel de ambiguidade, perguntas de discovery e checklist de validacao.
  - novo artefato `docs/27_descoberta_guiada.md` (diagnostico + perguntas priorizadas).
  - novo artefato `docs/28_validacao_pre_kickoff.md` (gate de prontidao antes de iniciar implementacao).
  - backlog dinamico priorizando discovery quando ambiguidade esta alta.
- Validacao:
  - `test:python` -> `37 passed`
  - `quality:python` -> `ok: true`
  - `runtime:check` -> `ok: true`
  - `audit:safety` -> `ok: true`
- Proxima etapa recomendada:
  - versionar thresholds comerciais de decisao por score/ambiguidade/gaps para padronizar aprovacao.

## Atualizacao Fase 3 - Etapa 16 (2026-03-11)

- Objetivo da etapa:
  - tornar a decisao comercial (`GO`, `GO_COM_RESSALVAS`, `NO_GO`) padronizada e versionada.
- Entregas:
  - policy engine em `src/ai_engineering_os/decision_policy.py`.
  - thresholds versionados em `config/decision_policy.json` (v1.0.0).
  - `IdeaValidator` integrado com decisao base + decisao final por policy.
  - quality gate com check `decision_policy_configured`.
  - documento de governanca: `docs/31_politica_decisao_comercial.md`.
- Validacao:
  - `test:python` -> `41 passed`
  - `quality:python` -> `ok: true`
  - `runtime:check` -> `ok: true`
  - `audit:safety` -> `ok: true`
- Proxima etapa recomendada:
  - calibrar thresholds por tipo de projeto e coletar historico de decisoes para ajuste fino.

## Como retomar rapido no Codex

1. Abrir terminal na pasta:
   - `C:\Users\Guilherme - Hogar\Desktop\agents\ai-engineering-system`
2. Executar:
   - `codex resume --last --no-alt-screen`
3. Na conversa, pedir:
   - "continuar do docs/18_codex_handoff.md e iniciar Fase 1"

## Observacao de seguranca

- Tokens que apareceram no chat devem ser revogados e substituidos.
