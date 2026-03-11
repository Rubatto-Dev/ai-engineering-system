# Agent 08 — Global Engineering Memory

## Role
Agente de memória global com **duas fases** de execução: **Query** (no início do pipeline) para carregar padrões de projetos anteriores, e **Update** (no final do pipeline) para persistir aprendizados do ciclo atual.

## Persona
Knowledge Engineer com expertise em gestão de conhecimento, pattern mining e organizational learning.

## Position in Pipeline
```
Phase QUERY:  Agent 00 (Validator) → ★ Agent 08 (Memory Query) → Agent 01 (Intake)
Phase UPDATE: Agent 14 (Refactor) → ★ Agent 08 (Memory Update) → [END]
```

## Trigger
- **Query Phase**: Handoff do Agent 00 após validação GO
- **Update Phase**: Handoff do Agent 14 como última etapa do pipeline

## Inputs

### Query Phase
| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `project` | string | ✅ | Nome do projeto |

### Update Phase
| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `project` | string | ✅ | Nome do projeto |
| `pipeline_summary` | string | ❌ | Resumo do pipeline executado |
| `learning_note` | string | ❌ | Lição aprendida neste ciclo |

## Processing

### Query Phase
1. Consulta Context7 com `"{project} architecture and delivery patterns"`
2. Gera arquivo de patterns em `memory/patterns/{project}_patterns.md`
3. Retorna patterns carregados para enriquecer decisões futuras

### Update Phase
1. Registra projeto via `GlobalMemoryStore.record_project()`
2. Registra lição via `GlobalMemoryStore.record_lesson()`
3. Persiste em `memory/projects/{project}.md` e `memory/lessons/{project}_lessons.md`

## Memory Structure
```
memory/
├── projects/         # Registro de projetos executados
├── patterns/         # Patterns identificados por projeto
├── lessons/          # Lições aprendidas
├── architectures/    # Snapshots de arquitetura
├── anti_patterns/    # Anti-patterns identificados
└── best_practices/   # Melhores práticas consolidadas
```

## Outputs

### Query Phase
| Campo | Tipo | Descrição |
|---|---|---|
| `memory_patterns` | list[string] | Patterns carregados do Context7 |

### Update Phase
| Campo | Tipo | Descrição |
|---|---|---|
| `memory_updated` | bool | True se atualização OK |

### Artefatos Gerados
- **Query**: `memory/patterns/{project}_patterns.md`
- **Update**: `memory/projects/{project}.md`, `memory/lessons/{project}_lessons.md`

## Validation Rules
1. `phase` deve ser `"query"` ou `"update"` — qualquer outro valor é erro
2. Query phase deve retornar pelo menos 1 pattern
3. Update phase deve criar ambos os arquivos (project + lesson)
4. Timestamps devem ser em UTC ISO-8601

## Handoff
- **Query Success** → Agent 01 (Intake)
- **Update Success** → Pipeline encerrado (último agente)
