# Requisitos

## Objetivo do produto

Entregar um sistema de orquestracao assistida por IA com protocolo Jarvis, rastreabilidade de artefatos e gates de qualidade antes de `ship`.

## Escopo

- Em escopo:
  - Execucao de ciclo Jarvis (`START`, `PLAN`, `EXEC`, `AUDIT`, `SHIP`)
  - Orquestracao de equipe de agentes com handoff rastreavel
  - Persistencia de documentacao e memoria operacional
  - Validacao de qualidade (testes, docs, seguranca e runtime externo)
- Fora de escopo na v1:
  - Deploy direto em producao
  - Integracao operacional com Trello (somente referencia de integracao)

## Requisitos funcionais

- `RF-001`: aceitar comandos no formato `JARVIS: <COMANDO> arg=value`.
- `RF-002`: em `START`, inicializar contexto de projeto e resetar estado de execucao/auditoria.
- `RF-003`: em `PLAN`, retornar etapas previstas e quantidade esperada de agentes.
- `RF-004`: em `EXEC`, executar pipeline completo com traces por etapa e lista de artefatos.
- `RF-005`: em `AUDIT`, avaliar quality gate com suporte a `strict_external=true`.
- `RF-006`: em `SHIP`, bloquear envio sem auditoria valida para a ultima execucao.
- `RF-007`: manter estrutura minima de repositorio (`docs`, `memory`, `config`, `schemas`).
- `RF-008`: persistir artefatos de doc e memoria com historico legivel.

## Requisitos nao funcionais

- `RNF-001` Confiabilidade: pipeline deve falhar de forma controlada e com motivo explicito.
- `RNF-002` Testabilidade: cobertura minima em 3 camadas (`unit`, `integration`, `e2e`).
- `RNF-003` Auditabilidade: toda etapa deve incluir `handoff` e `checks` no trace.
- `RNF-004` Qualidade: quality gate deve validar docs, seguranca, ADR e configuracao de tooling.
- `RNF-005` Operacao: runtime check deve validar Node, npm, MCPs e SonarQube API.

## Criterios observaveis de sucesso (Fase 1)

- `npm run test:python` executa com sucesso.
- `npm run quality:python` retorna `ok: true`.
- `npm run runtime:check` retorna `ok: true`.
- Contrato Jarvis documentado em API/arquitetura/modelo de dados com rastreabilidade.
