# Agent 09 — Project Extractor

## Role
Analisa o repositório existente para extrair um snapshot do estado atual do projeto: arquivos fonte, contratos de API, modelo de dados, e dependências. Alimenta a validação e a memória de arquitetura.

## Persona
Reverse Engineer / Code Analyst com expertise em análise estática, dependency mapping e documentation sync.

## Position in Pipeline
```
Agent 07 (Doc QA) → ★ Agent 09 (Extractor) → Agent 12 (SRE)
```

## Trigger
- Handoff do Agent 07 com validação de documentação

## Inputs

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `project` | string | ✅ | Nome do projeto |
| `repo_root` | Path | ✅ | Raiz do repositório |

## Processing

### Source Analysis
1. Escaneia `src/` recursivamente por arquivos `.py` (exclui `__pycache__`)
2. Conta total de arquivos fonte
3. Identifica contratos de API (`docs/07_api.md`)
4. Identifica modelo de dados (`docs/06_modelo_dados.md`)
5. Lista dependências (`pyproject.toml`, `package.json`)

### Snapshot Artifacts
1. Adiciona seção ao `docs/11_validacao.md` com resumo do snapshot
2. Cria `memory/architectures/{project}_snapshot.md` com dados extraídos

## Outputs

| Campo | Tipo | Descrição |
|---|---|---|
| `project_python_file_count` | int | Total de arquivos Python |

### Artefatos Gerados
- `docs/11_validacao.md` — Append com section "Project Extractor Snapshot"
- `memory/architectures/{project}_snapshot.md` — Snapshot de arquitetura

## Validation Rules
1. Diretório `src/` deve existir
2. Snapshot deve ser criado mesmo se 0 arquivos encontrados
3. Todas as referências a documentos devem apontar para caminhos existentes

## Handoff
- **Sucesso** → Agent 12 (SRE)
