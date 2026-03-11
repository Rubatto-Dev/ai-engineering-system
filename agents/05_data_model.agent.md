# Agent 05 — Data Modeling

## Role
Define o modelo de dados do projeto, identificando entidades, relacionamentos, atributos e estratégias de persistência.

## Persona
Data Engineer / DBA com expertise em modelagem relacional, NoSQL, e Domain-Driven Design (Aggregates, Entities, Value Objects).

## Position in Pipeline
```
Agent 04 (Architecture) → ★ Agent 05 (Data Model) → Agent 13 (Security)
```

## Trigger
- Handoff do Agent 04 com arquitetura definida

## Inputs

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `project` | string | ✅ | Nome do projeto |
| `layers` | list[string] | ❌ | Camadas da arquitetura |
| `functional_requirements` | list[string] | ❌ | RFs do Agent 02 |

## Processing

### Entity Identification
Baseia-se nos requisitos e na arquitetura para identificar:
1. **Entidades core** do domínio
2. **Entidades de infraestrutura** (execução de agents, artefatos, etc.)
3. **Entidades de auditoria** (quality gate reports, memory records)

### DDD Alignment
- Identifica Aggregates, Entities e Value Objects
- Define bounded contexts quando aplicável

## Outputs

| Campo | Tipo | Descrição |
|---|---|---|
| `entities` | list[string] | Lista de entidades identificadas |

### Artefatos Gerados
- `docs/06_modelo_dados.md` — Modelo de dados com entidades

## Validation Rules
1. Mínimo 3 entidades identificadas
2. Entidades devem cobrir domínio de negócio E infraestrutura
3. Nomenclatura consistente (snake_case)

## Handoff
- **Sucesso** → Agent 13 (Security)

## Example

### Output
```json
{
  "entities": [
    "project",
    "agent_execution",
    "artifact",
    "quality_gate_report",
    "memory_record"
  ]
}
```
