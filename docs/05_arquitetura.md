# Arquitetura

## Visao geral

Arquitetura em camadas com protocolo Jarvis como ponto de entrada, orquestracao de agentes no core da aplicacao e adaptadores de infraestrutura para qualidade, runtime e persistencia de artefatos.

## Camadas e responsabilidades

- `entrypoints`
  - `cli.py`: entrada de comando em shell.
  - `command_protocol.py`: parse e validacao de comandos Jarvis.
- `application`
  - `jarvis.py`: maquina de estados do ciclo (`start/plan/exec/audit/ship`).
  - `pipeline.py`: orquestracao dos agentes e consolidacao de traces.
- `domain`
  - `models.py`: contratos de `ProjectContext`, `AgentResult`, `StageTrace`.
  - `agents/*`: regras por etapa e handoff entre agentes.
- `infrastructure`
  - `repository.py`: bootstrap de estrutura minima e docs obrigatorios.
  - `quality_gate.py`: validacoes de docs, tooling e seguranca.
  - `external_runtime.py`: probes de Node/npm/MCP/SonarQube.
  - `memory_store.py`: armazenamento de memoria operacional.

## Fluxo principal (comando para resultado)

1. Usuario envia comando `JARVIS: ...` via CLI.
2. Parser valida comando e argumentos obrigatorios.
3. `JarvisEngine` roteia para acao correspondente.
4. `EXEC` dispara pipeline com equipe de agentes e coleta de artefatos.
5. Cada agente passa por `enforce_contract`, publica `handoff_packet` e so avanca com `stage_validation_ok=true`.
6. `AUDIT` aplica quality gate e, opcionalmente, runtime externo estrito.
7. `SHIP` somente libera quando auditoria da ultima execucao esta valida.

## Integracoes

- `Context7 MCP`: enriquecimento de contexto para planejamento e requisitos.
- `Sequential Thinking MCP`: decomposicao estruturada de etapas e decisoes.
- `GitHub MCP`: operacao de repositorio remoto (issues, PRs, arquivos).
- `SonarQube`: quality gate externo e sinal de saude operacional.
- `Trello MCP`: previsto em arquitetura, ainda fora do escopo operacional da v1.

## Decisoes arquiteturais da Fase 1

- Gate de `ship` depende de `audit` da ultima execucao para evitar release desatualizada.
- Estrutura de docs obrigatoria garante rastreabilidade minima do ciclo.
- Runtime check foi endurecido para nunca quebrar a execucao por excecao transiente HTTP.

## Referencias Context7

- `context7:strict_ok_demo_clean_architecture_api_first:official_docs`
- `context7:strict_ok_demo_clean_architecture_api_first:reference_patterns`
- `context7:strict_ok_demo_clean_architecture_api_first:known_pitfalls`
