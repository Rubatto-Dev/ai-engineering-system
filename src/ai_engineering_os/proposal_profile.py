from __future__ import annotations

from pathlib import Path
import re
from typing import Any


_TYPE_KEYWORDS = {
    "frontend": [
        "frontend",
        "interface",
        "ui",
        "ux",
        "landing",
        "web",
        "mobile",
        "react",
        "next.js",
        "nextjs",
    ],
    "backend": [
        "backend",
        "api",
        "database",
        "postgres",
        "auth",
        "server",
        "microservice",
        "integration",
        "etl",
    ],
    "automacao": [
        "automation",
        "automacao",
        "workflow",
        "n8n",
        "zapier",
        "bot",
        "whatsapp",
        "cron",
    ],
}

_KNOWN_INTEGRATIONS = [
    "github",
    "slack",
    "discord",
    "whatsapp",
    "twilio",
    "stripe",
    "mercado pago",
    "openai",
    "notion",
    "trello",
    "hubspot",
    "salesforce",
    "google sheets",
]

_STACK_BY_TYPE = {
    "frontend": ["TypeScript", "React", "Next.js", "Playwright", "Tailwind CSS"],
    "backend": ["Python 3.11", "FastAPI", "PostgreSQL", "Pytest", "Docker"],
    "automacao": ["Python 3.11", "n8n", "Redis", "Webhook APIs", "Pytest"],
    "hibrido": ["Python 3.11", "FastAPI", "TypeScript", "React", "PostgreSQL", "Docker", "Pytest"],
}


def load_proposal_text(repo_root: Path, proposal_file: str | None) -> tuple[str | None, str | None]:
    if not proposal_file:
        return None, None

    candidate = Path(proposal_file)
    if not candidate.is_absolute():
        candidate = (repo_root / candidate).resolve()

    if not candidate.exists() or not candidate.is_file():
        return None, None

    text = candidate.read_text(encoding="utf-8").strip()
    if not text:
        return str(_display_path(repo_root, candidate)), ""

    return str(_display_path(repo_root, candidate)), text


def build_proposal_profile(project: str, proposal_text: str | None) -> dict[str, Any]:
    text = (proposal_text or "").strip()
    if not text:
        return _default_profile(project)

    normalized = text.lower()
    features = _extract_feature_lines(text)
    integrations = _extract_integrations(normalized)
    project_type = _infer_project_type(normalized)
    clarity = _estimate_clarity(normalized, features)
    complexity = _estimate_complexity(features, integrations, normalized)
    feasibility = _infer_feasibility(clarity, complexity)
    duration = _estimate_duration(project_type, complexity)
    value_statement = _extract_value_statement(text, project)
    value_score = _estimate_value(features, integrations, normalized)
    missing_info = _missing_information(normalized)
    assumptions = _assumptions(project_type, missing_info)
    risks = _risks(complexity, integrations, missing_info)

    return {
        "source": "proposal_text",
        "proposal_present": True,
        "project": project,
        "project_type": project_type,
        "value_hypothesis": value_statement,
        "value_score": value_score,
        "clarity_score": clarity,
        "complexity_score": complexity,
        "feasibility": feasibility,
        "estimated_duration_weeks": duration,
        "recommended_stack": _STACK_BY_TYPE[project_type],
        "key_features": features[:8],
        "integrations": integrations,
        "missing_information": missing_info,
        "assumptions": assumptions,
        "risks": risks,
        "confidence": _confidence(clarity, missing_info),
    }


def _default_profile(project: str) -> dict[str, Any]:
    return {
        "source": "default_assumptions",
        "proposal_present": False,
        "project": project,
        "project_type": "hibrido",
        "value_hypothesis": f"Deliver measurable engineering value for {project} with controlled risk.",
        "value_score": 0.62,
        "clarity_score": 0.55,
        "complexity_score": 0.45,
        "feasibility": "media",
        "estimated_duration_weeks": {"min": 4, "avg": 6, "max": 8},
        "recommended_stack": _STACK_BY_TYPE["hibrido"],
        "key_features": [
            "Structured project intake and feasibility assessment",
            "Requirements, scope, and architecture baseline",
            "Quality gate and runtime validation before execution",
        ],
        "integrations": ["sonarqube", "context7", "sequential-thinking", "github"],
        "missing_information": [
            "target_users",
            "budget",
            "deadline",
            "success_metrics",
            "compliance_constraints",
        ],
        "assumptions": [
            "Initial discovery workshop will clarify business priorities.",
            "Environment and tool access will be provided before execution.",
        ],
        "risks": [
            "Scope drift from unclear success criteria.",
            "Environment dependency delays for external integrations.",
        ],
        "confidence": "media",
    }


def _extract_feature_lines(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    bullet_features: list[str] = []
    for line in lines:
        if re.match(r"^[-*]\s+", line) or re.match(r"^\d+[.)]\s+", line):
            cleaned = re.sub(r"^[-*]\s+|^\d+[.)]\s+", "", line).strip()
            if len(cleaned) >= 8:
                bullet_features.append(cleaned)

    if bullet_features:
        return _unique_keep_order(bullet_features)

    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    if not sentences:
        return ["Projeto com requisitos a detalhar em discovery."]

    return _unique_keep_order(sentences[1:6] if len(sentences) > 1 else sentences[:1])


def _extract_integrations(normalized_text: str) -> list[str]:
    found = [item for item in _KNOWN_INTEGRATIONS if item in normalized_text]
    return _unique_keep_order(found)


def _infer_project_type(normalized_text: str) -> str:
    scores: dict[str, int] = {}
    for project_type, words in _TYPE_KEYWORDS.items():
        scores[project_type] = sum(1 for word in words if word in normalized_text)

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_type, top_score = ranked[0]
    second_score = ranked[1][1]

    if top_score == 0:
        return "hibrido"
    if second_score > 0 and abs(top_score - second_score) <= 1:
        return "hibrido"
    return top_type


def _estimate_clarity(normalized_text: str, features: list[str]) -> float:
    score = 0.35
    if any(word in normalized_text for word in ["objetivo", "goal", "resultado"]):
        score += 0.15
    if any(word in normalized_text for word in ["escopo", "scope", "in scope", "out of scope"]):
        score += 0.10
    if any(word in normalized_text for word in ["prazo", "deadline", "timeline", "semanas", "weeks"]):
        score += 0.10
    if any(word in normalized_text for word in ["orcamento", "budget", "custo", "cost"]):
        score += 0.10
    if any(word in normalized_text for word in ["kpi", "metric", "sucesso", "success"]):
        score += 0.10
    score += min(0.20, len(features) * 0.03)
    return round(min(0.95, score), 2)


def _estimate_complexity(features: list[str], integrations: list[str], normalized_text: str) -> float:
    score = 0.30
    score += min(0.30, len(features) * 0.04)
    score += min(0.25, len(integrations) * 0.06)
    if any(token in normalized_text for token in ["realtime", "real-time", "high availability", "multi tenant"]):
        score += 0.10
    if any(token in normalized_text for token in ["compliance", "lgpd", "hipaa", "pci"]):
        score += 0.10
    return round(min(0.90, score), 2)


def _infer_feasibility(clarity: float, complexity: float) -> str:
    if clarity >= 0.65 and complexity <= 0.60:
        return "alta"
    if clarity < 0.45 and complexity > 0.75:
        return "baixa"
    return "media"


def _estimate_duration(project_type: str, complexity: float) -> dict[str, int]:
    base_weeks = {
        "frontend": 4,
        "backend": 6,
        "automacao": 5,
        "hibrido": 8,
    }[project_type]
    avg = max(2, int(round(base_weeks * (0.85 + complexity * 0.9))))
    min_weeks = max(2, int(round(avg * 0.75)))
    max_weeks = max(min_weeks + 1, int(round(avg * 1.35)))
    return {"min": min_weeks, "avg": avg, "max": max_weeks}


def _extract_value_statement(text: str, project: str) -> str:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    if sentences:
        first = sentences[0]
        return first[:220]
    return f"Increase delivery confidence and measurable business value for {project}."


def _estimate_value(features: list[str], integrations: list[str], normalized_text: str) -> float:
    score = 0.45
    score += min(0.25, len(features) * 0.04)
    score += min(0.12, len(integrations) * 0.03)
    if any(word in normalized_text for word in ["revenue", "receita", "vendas", "conversao"]):
        score += 0.10
    if any(word in normalized_text for word in ["reduzir custo", "efficiency", "produtividade", "automacao"]):
        score += 0.08
    return round(min(0.95, score), 2)


def _missing_information(normalized_text: str) -> list[str]:
    checks = [
        ("target_users", ["usuario", "users", "persona", "cliente final"]),
        ("budget", ["orcamento", "budget", "custo", "cost"]),
        ("deadline", ["prazo", "deadline", "timeline", "sprint"]),
        ("success_metrics", ["kpi", "metric", "metrica", "sucesso", "success"]),
        ("non_functional_requirements", ["latencia", "availability", "sla", "performance"]),
        ("compliance_constraints", ["lgpd", "compliance", "pci", "hipaa", "security"]),
    ]
    missing: list[str] = []
    for key, tokens in checks:
        if not any(token in normalized_text for token in tokens):
            missing.append(key)
    return missing


def _assumptions(project_type: str, missing_info: list[str]) -> list[str]:
    assumptions = [
        f"Primary delivery track starts as {project_type}.",
        "Documentation and validation happen before implementation starts.",
    ]
    if missing_info:
        assumptions.append("Open discovery questions must be closed before final estimate commitment.")
    return assumptions


def _risks(complexity: float, integrations: list[str], missing_info: list[str]) -> list[str]:
    risks: list[str] = []
    if complexity >= 0.70:
        risks.append("High technical complexity may affect estimate confidence.")
    if len(integrations) >= 3:
        risks.append("Multiple external integrations increase dependency risk.")
    if len(missing_info) >= 3:
        risks.append("Critical discovery gaps may invalidate early planning assumptions.")
    if not risks:
        risks.append("No critical blockers identified with current proposal data.")
    return risks


def _confidence(clarity: float, missing_info: list[str]) -> str:
    if clarity >= 0.70 and len(missing_info) <= 2:
        return "alta"
    if clarity < 0.45 or len(missing_info) >= 5:
        return "baixa"
    return "media"


def _display_path(repo_root: Path, path: Path) -> Path:
    try:
        return path.relative_to(repo_root)
    except ValueError:
        return path


def _unique_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        ordered.append(item.strip())
    return ordered
