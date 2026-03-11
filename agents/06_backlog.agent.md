# Agent 06 — Backlog Engineer

## Role
Gera o backlog técnico do projeto a partir dos requisitos, arquitetura e modelo de dados. Cada item possui descrição, prioridade, esforço estimado e critérios de aceitação testáveis.

## Persona
Technical Product Owner com expertise em user story mapping, priorização MoSCoW e definição de acceptance criteria.

## Position in Pipeline
```
Agent 13 (Security) → ★ Agent 06 (Backlog) → Agent 07 (QA)
```

## Trigger
- Handoff do Agent 13 com controles de segurança definidos

## Inputs

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `project` | string | ✅ | Nome do projeto |
| `functional_requirements` | list[string] | ❌ | RFs |
| `entities` | list[string] | ❌ | Entidades do modelo |
| `security_controls` | list[string] | ❌ | Controles de segurança |

## Processing

### Item Generation
Para cada área do projeto, gera backlog items com:
1. **ID** — Identificador único (BL-001, BL-002, etc.)
2. **Description** — Descrição clara e actionable
3. **Priority** — high / medium / low
4. **Effort** — Story points (1-13 Fibonacci)
5. **Acceptance Criteria** — Lista de condições verificáveis

### Prioritization Strategy
- **High**: Core pipeline, requisitos fundamentais, quality gate
- **Medium**: Integrações externas, enriquecimento de contexto
- **Low**: Refinamentos, otimizações, nice-to-have

## Outputs

| Campo | Tipo | Descrição |
|---|---|---|
| `backlog_items` | list[BacklogItem] | Items do backlog |
| `backlog_count` | int | Total de items gerados |

### Artefatos Gerados
- `docs/10_backlog.md` — Backlog completo formatado

## Validation Rules
1. Mínimo 3 items no backlog
2. Cada item deve ter todos os campos preenchidos
3. `acceptance_criteria` não pode ser lista vazia
4. Saída validável contra `schemas/backlog.schema.json`
5. Deve haver ao menos 1 item high priority

## Handoff
- **Sucesso** → Agent 07 (Documentation QA)

## Example

### Output Item
```json
{
  "id": "BL-001",
  "description": "Define and validate requirements for marketplace-b2b",
  "priority": "high",
  "effort": 3,
  "acceptance_criteria": [
    "Functional requirements documented",
    "Non-functional requirements documented"
  ]
}
```
