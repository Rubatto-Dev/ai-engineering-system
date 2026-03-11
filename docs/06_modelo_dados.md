# Modelo de Dados

## Entidades principais

### project
- `project_name` (string, pk logica)
- `current_cycle` (int)
- `mode` (string)
- `started_at` (date/datetime)
- `status` (started | planned | running | audited | shipped | blocked)

### agent_execution
- `project_name` (string, fk logica -> project)
- `cycle` (int)
- `agent_id` (string, ex: `00`..`14`)
- `agent_name` (string)
- `stage` (string)
- `status` (success | failed)
- `checks` (map)
- `handoff` (string)
- `notes` (string)

### artifact
- `project_name` (string)
- `cycle` (int)
- `path` (string)
- `artifact_type` (doc | memory | report | decision)
- `generated_by_agent` (string)

### quality_gate_report
- `project_name` (string)
- `cycle` (int, opcional em auditoria manual)
- `tests_ok` (bool)
- `security_checks_ok` (bool)
- `quality_gate_ok` (bool)
- `docs_updated` (bool)
- `adr_updated` (bool)
- `external_runtime_ok` (bool, quando `strict_external=true`)
- `overall_ok` (bool)

### memory_record
- `project_name` (string)
- `bucket` (projects | lessons | patterns | architectures | anti_patterns | best_practices)
- `file_path` (string)
- `summary` (string)
- `updated_at` (datetime)

## Relacionamentos

- `project 1:N agent_execution`
- `project 1:N artifact`
- `project 1:N quality_gate_report`
- `project 1:N memory_record`

## Observacao

O sistema atual persiste principalmente em arquivos (`docs/` e `memory/`), e este modelo representa o contrato logico para rastreabilidade e evolucao futura.
