# Backlog

## Fase 1 - Escopo minimo (inicio em 2026-03-11)

- Objetivo: consolidar baseline de requisitos + arquitetura e iniciar validacao operacional do strict_ok_demo.
- Criterios globais de sucesso:
  - Requisitos funcionais e nao funcionais rastreaveis em docs.
  - Arquitetura, API e modelo de dados alinhados ao protocolo Jarvis.
  - `npm run test:python` e `npm run quality:python` executando com sucesso.
  - `npm run runtime:check` com `ok: true` ou bloqueio externo registrado com dono e proxima acao.

## Priorizacao por risco tecnico e dependencia

1. `BL-001` (alto impacto, desbloqueia contratos e arquitetura)
2. `BL-002` (alto impacto, base para validacao de integracao)
3. `BL-003` (alto impacto, validacao operacional e runtime externo)
4. `BL-004` (medio impacto, parcialmente concluido)

## Itens

### BL-001 - Definir e validar requisitos de strict_ok_demo
- priority: high
- effort: 3
- phase: 1
- status: done
- dependencies: none
- acceptance_criteria:
  - Requisitos funcionais documentados
  - Requisitos nao funcionais documentados
  - Escopo e fora de escopo explicitados
- evidencias:
  - docs/01_visao.md
  - docs/02_requisitos.md
  - docs/19_fase1_status.md

### BL-002 - Consolidar baseline de arquitetura e contratos de API
- priority: high
- effort: 5
- phase: 1
- status: done
- dependencies:
  - BL-001
- acceptance_criteria:
  - Arquitetura atualizada por camadas e integracoes
  - Contratos de API descritos por comando Jarvis
  - Modelo de dados conectado aos contratos
- evidencias:
  - docs/05_arquitetura.md
  - docs/06_modelo_dados.md
  - docs/07_api.md
  - tests/integration/test_pipeline_integration.py

### BL-003 - Validar piramide de testes e quality gate operacional
- priority: high
- effort: 5
- phase: 1
- status: done
- dependencies:
  - BL-002
- acceptance_criteria:
  - Unit, integration e e2e passando
  - Quality gate retornando sucesso
  - Runtime check com SonarQube alcancavel
- evidencias:
  - npm run test:python
  - npm run quality:python
  - npm run runtime:check
  - runtime check com `ok: true` em 2026-03-11
- resolucao:
  - Docker Desktop iniciado e SonarQube local ativo
  - robustez extra no probe Sonar para nao interromper runtime check em erro transiente de conexao

### BL-004 - Integrar Context7 e Sequential-Thinking no caminho de planejamento
- priority: medium
- effort: 3
- phase: 1
- status: done
- dependencies: none
- acceptance_criteria:
  - Context enrichment disponivel
  - Rastro de planejamento sequencial registrado em validacao
- evidencias:
  - config/mcp-servers.json
  - docs/11_validacao.md

## Ciclo atual

- Tarefa principal: executar Fase 2 em microetapas com validacao por etapa.
- Etapas concluidas em 2026-03-11:
  - etapa 1: ampliar testes de failure-mode do runtime externo (agregador de readiness)
  - etapa 2: reforcar contrato tipado de `AgentResult` no `enforce_contract`
  - etapa 3: validar falha de handoff por contrato no pipeline (teste de integracao)
  - etapa 4: ampliar cenarios de auditoria estrita (`strict_external`) e bloqueio de ship
  - etapa 5: consolidar pacote de auditoria de release safety com evidencia automatica
  - etapa 6: consolidar changelog tecnico e criterios de aceite da Fase 2
  - etapa 7: criar branch, commit e publicar PR interno de consolidacao
  - etapa 8: publicar checklist de revisao e criterio de merge do PR
  - etapa 9: consolidar plano de risco e rollback para merge seguro
  - etapa 10: emitir recomendacao final de merge com evidencias de gate
- Proxima etapa:
  - etapa 11: executar merge no PR e registrar release notes finais
