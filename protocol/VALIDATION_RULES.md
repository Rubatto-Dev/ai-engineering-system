# Validation Rules

These rules define the mandatory checks that must pass before `JARVIS: SHIP` is allowed.

## Ship Gate Requirements

### 1. Test Pyramid (tests_ok)
All three test layers must pass:

| Layer | Location | Marker | Minimum |
|---|---|---|---|
| Unit | `tests/unit/` | `@pytest.mark.unit` | Must pass |
| Integration | `tests/integration/` | `@pytest.mark.integration` | Must pass |
| E2E | `tests/e2e/` | `@pytest.mark.e2e` | Must pass |

Command: `pytest --strict-markers`

### 2. Documentation Completeness (docs_updated)
All 16 mandatory documents must:
- Exist in the `docs/` directory
- Have non-empty content (not just headers)

Required documents:
```
01_visao.md          02_requisitos.md      03_regras_de_negocio.md
04_fluxos.md         05_arquitetura.md     06_modelo_dados.md
07_api.md            08_seguranca.md       09_riscos.md
10_backlog.md        11_validacao.md       12_roadmap.md
13_deploy.md         14_observability.md   15_security_threats.md
16_release_notes.md
```

### 3. Security Checks (security_checks_ok)
- Security Agent (13) must have executed successfully
- Threat modeling completed
- Security controls documented
- Risk document updated with security complement

### 4. Quality Gate (quality_gate_ok)
SonarQube analysis must pass with:
- No critical or blocker issues
- Code coverage above project threshold
- No security vulnerabilities
- No code smells above threshold

### 5. ADR Updated (adr_updated)
- At least `docs/decisions/ADR-0001.md` must exist
- ADR must follow the Context / Decision / Consequences format

## Validation Flow

```
JARVIS: AUDIT
    │
    ├─ Check tests_ok ──────────── fail? → audit_failed
    ├─ Check docs_updated ───────── fail? → audit_failed
    ├─ Check security_checks_ok ── fail? → audit_failed
    ├─ Check quality_gate_ok ────── fail? → audit_failed
    └─ Check adr_updated ────────── fail? → audit_failed
    │
    └─ All passed → audit_ok
```

## Ship Blocking Policy
If ANY check fails:
1. `JARVIS: SHIP` returns `ship_blocked`
2. Response includes which checks failed
3. Team must fix issues and re-run `JARVIS: AUDIT`
4. SHIP is only allowed after `audit_ok`
