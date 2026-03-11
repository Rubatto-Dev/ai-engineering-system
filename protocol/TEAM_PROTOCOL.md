# Team Protocol

## Source of Truth
The document `AI_ENGINEERING_OS.md` is the single source of truth for all system behavior. In case of conflict, it takes precedence over individual agent specs, prompts, or code.

## Pipeline Execution Rules

### 1. Sequential Execution
- Agents execute in strict order as defined by `build_agent_team()` in `agents/team.py`
- No agent may start before the previous agent has completed successfully
- The pipeline halts immediately if any agent returns `status: "failed"`

### 2. Handoff Protocol
- Every agent MUST specify a `handoff` field pointing to the next agent's ID
- The pipeline orchestrator validates the handoff chain at startup
- If a handoff target doesn't match the next agent in the list, a `WARNING` is logged

### 3. State Propagation
- Each agent receives a shared `state` dictionary
- Agents add their outputs to `state` via the `outputs` field of `AgentResult`
- Downstream agents can read upstream outputs from the state
- State is NOT persisted between pipeline runs — each run starts fresh

## Quality Gate Agreement

### Pre-Ship Checklist
Before any `JARVIS: SHIP` command is accepted:
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All e2e tests passing
- [ ] SonarQube quality gate: passed
- [ ] All 16 required documents present and non-empty
- [ ] At least 1 ADR created and current
- [ ] Security checks approved
- [ ] Documentation QA agent returned `ok: true`

### Quality Gate Failure
If the quality gate fails:
1. `SHIP` command returns `ship_blocked`
2. Failure reason is documented in the response
3. The team must fix the issues and re-run `JARVIS: AUDIT`

## Tool Integration

### Required MCP Servers
| Server | Role | Usage |
|---|---|---|
| Context7 | Context enrichment | Planning, architecture, requirements |
| Sequential Thinking | Structured reasoning | Decomposition, validation, roadmap |
| SonarQube | Quality gate | Pre-ship validation |
| Trello | Task management | Backlog sync, task tracking |

### Tool Usage Policy
- Context7 MUST be used by: Agent 04 (Architecture), Agent 08 (Memory Query)
- Sequential Thinking MUST be used by: Agent 07 (Doc QA), Agent 11 (PM)
- SonarQube is required for `JARVIS: AUDIT` and `JARVIS: SHIP`
- Trello integration is used for backlog export (Agent 06)

## Engineering Standards
All code and documentation must conform to:
- **SOLID** principles
- **Clean Architecture** (dependency rule)
- **Clean Code** (readability, small functions, meaningful names)
- **DDD** (when domain complexity justifies it)
- **API First** (contracts before implementation)
- **Documentation Driven Development** (docs before code)
