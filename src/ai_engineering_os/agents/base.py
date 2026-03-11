from __future__ import annotations

import hashlib
import logging
import re
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..memory_store import GlobalMemoryStore
from ..models import AgentResult, ProjectContext

logger = logging.getLogger("ai_engineering_os.agents")


@dataclass
class BacklogItem:
    item_id: str
    description: str
    priority: str
    effort: int
    acceptance_criteria: list[str]


class AgentExecutionError(RuntimeError):
    """Raised when an agent fails with a non-recoverable issue."""


class Context7Adapter:
    """Deterministic context adapter placeholder for Context7 integration."""

    def lookup(self, topic: str) -> list[str]:
        normalized = topic.strip().lower().replace(" ", "_")
        return [
            f"context7:{normalized}:official_docs",
            f"context7:{normalized}:reference_patterns",
            f"context7:{normalized}:known_pitfalls",
        ]


class SequentialThinkingAdapter:
    """Deterministic step decomposition placeholder."""

    def decompose(self, objective: str, steps: list[str] | None = None) -> list[str]:
        if steps:
            return [f"{idx + 1}. {step}" for idx, step in enumerate(steps)]

        base = [
            "Clarify goal and constraints",
            "Break work into traceable chunks",
            "Prioritize by risk and impact",
            "Define validation for each chunk",
            "Execute and verify outputs",
        ]
        return [f"{idx + 1}. {step} ({objective})" for idx, step in enumerate(base)]


class _NoopMemoryStore:
    def record_project(self, project: str, summary: str) -> Path:
        return Path(f"memory/projects/{project}_noop.md")

    def record_lesson(self, project: str, lesson: str) -> Path:
        return Path(f"memory/lessons/{project}_noop.md")


class BaseAgent:
    agent_id = ""
    agent_name = ""
    stage = ""
    _default_contract_root = Path(__file__).resolve().parents[3] / "agents"
    _required_contract_sections = ["Role", "Inputs", "Processing", "Outputs", "Handoff"]
    _required_handoff_packet_sections = [
        "from_agent_id",
        "from_agent_name",
        "from_stage",
        "to_agent_id",
        "status",
        "summary",
        "artifacts",
        "open_questions",
        "assumptions",
        "risks",
        "validation_snapshot",
        "validated_at_utc",
    ]

    def __init__(
        self,
        repo_root: Path | None = None,
        context7: Context7Adapter | None = None,
        sequential: SequentialThinkingAdapter | None = None,
        memory_store: GlobalMemoryStore | _NoopMemoryStore | None = None,
    ) -> None:
        self.repo_root = repo_root or Path(".")
        self.context7 = context7 or Context7Adapter()
        self.sequential = sequential or SequentialThinkingAdapter()
        self.memory_store = memory_store or _NoopMemoryStore()

    def run(self, context: ProjectContext, state: dict[str, Any]) -> AgentResult:
        raise NotImplementedError

    def enforce_contract(self, result: AgentResult) -> AgentResult:
        original_notes_present = isinstance(result.notes, str) and bool(result.notes.strip())
        result.checks["initial_notes_present"] = original_notes_present

        schema_errors = self._validate_result_shape(result)
        result.checks["result_schema_ok"] = not schema_errors
        result.checks["result_schema_errors"] = schema_errors
        if schema_errors:
            result.status = "failed"
            error_text = ",".join(schema_errors)
            issue = f"result_schema_invalid={error_text}"
            result.notes = f"{result.notes}; {issue}" if result.notes else issue

        contract = self._load_contract()
        if not contract:
            result.checks["contract_loaded"] = False
            result.checks["contract_required_sections_ok"] = False
            result.checks["contract_missing_sections"] = self._required_contract_sections
            result.checks["contract_handoff_match"] = False
            result.checks["contract_expected_handoff"] = ""
            issue = "contract_file_missing"
            result.status = "failed"
            result.notes = f"{result.notes}; {issue}" if result.notes else issue
        else:
            contract_path, contract_text = contract
            phase = self._contract_phase()
            expected_handoff = self._expected_handoff(contract_text, phase)

            result.checks["contract_loaded"] = True
            result.checks["contract_file"] = contract_path.name
            result.checks["contract_sha256"] = hashlib.sha256(contract_text.encode("utf-8")).hexdigest()[:12]
            missing_sections = [
                section for section in self._required_contract_sections if not self._extract_section(contract_text, section)
            ]
            result.checks["contract_required_sections_ok"] = not missing_sections
            result.checks["contract_missing_sections"] = missing_sections
            if missing_sections:
                result.status = "failed"
                missing_text = ",".join(missing_sections)
                issue = f"contract_sections_missing={missing_text}"
                result.notes = f"{result.notes}; {issue}" if result.notes else issue

            if expected_handoff is None:
                result.checks["contract_handoff_match"] = True
                result.checks["contract_expected_handoff"] = ""
            else:
                result.checks["contract_expected_handoff"] = expected_handoff
                match = result.handoff == expected_handoff
                result.checks["contract_handoff_match"] = match
                if not match:
                    expected = expected_handoff or "[END]"
                    actual = result.handoff or "[END]"
                    mismatch = f"contract_handoff_mismatch expected={expected} actual={actual}"
                    result.status = "failed"
                    result.notes = f"{result.notes}; {mismatch}" if result.notes else mismatch

        handoff_errors = self._ensure_handoff_packet(result)
        result.checks["handoff_packet_ok"] = not handoff_errors
        result.checks["handoff_packet_errors"] = handoff_errors
        if handoff_errors:
            issue = f"handoff_packet_invalid={','.join(handoff_errors)}"
            result.status = "failed"
            result.notes = f"{result.notes}; {issue}" if result.notes else issue

        stage_requirements = self._stage_validation_requirements(result)
        stage_validation_ok = all(stage_requirements.values())
        result.checks["stage_validation_requirements"] = stage_requirements
        result.checks["stage_validation_ok"] = stage_validation_ok
        result.checks["stage_validation_missing"] = [key for key, value in stage_requirements.items() if not value]
        if not stage_validation_ok:
            issue = f"stage_not_fully_validated={','.join(result.checks['stage_validation_missing'])}"
            result.status = "failed"
            result.notes = f"{result.notes}; {issue}" if result.notes else issue
        return result

    def _validate_result_shape(self, result: AgentResult) -> list[str]:
        errors: list[str] = []

        if not isinstance(result.agent_id, str) or not result.agent_id.strip():
            errors.append("agent_id_missing")
        elif result.agent_id != self.agent_id:
            errors.append(f"agent_id_mismatch_expected_{self.agent_id}")

        if not isinstance(result.agent_name, str) or not result.agent_name.strip():
            errors.append("agent_name_missing")

        if not isinstance(result.stage, str) or not result.stage.strip():
            errors.append("stage_missing")

        if not isinstance(result.status, str) or not result.status.strip():
            errors.append("status_missing")

        if not isinstance(result.outputs, dict):
            errors.append("outputs_not_dict")

        if not isinstance(result.checks, dict):
            errors.append("checks_not_dict")

        if not isinstance(result.artifacts, list):
            errors.append("artifacts_not_list")
        elif any(not isinstance(item, str) for item in result.artifacts):
            errors.append("artifacts_non_string_item")

        if not isinstance(result.handoff, str):
            errors.append("handoff_not_string")
        elif result.handoff and not re.fullmatch(r"\d{2}", result.handoff):
            errors.append("handoff_invalid_format")

        return errors

    def _load_contract(self) -> tuple[Path, str] | None:
        pattern = f"{self.agent_id}_*.agent.md"
        roots = [self.repo_root / "agents", self._default_contract_root]

        seen: set[Path] = set()
        for root in roots:
            if root in seen:
                continue
            seen.add(root)
            if not root.exists():
                continue
            matches = sorted(root.glob(pattern))
            if not matches:
                continue
            path = matches[0]
            return path, path.read_text(encoding="utf-8")
        return None

    def _contract_phase(self) -> str | None:
        phase = getattr(self, "phase", None)
        return phase if isinstance(phase, str) else None

    def _expected_handoff(self, contract_text: str, phase: str | None) -> str | None:
        handoff_section = self._extract_section(contract_text, "Handoff")
        if not handoff_section:
            return None

        lines = [line.strip() for line in handoff_section.splitlines() if line.strip()]
        if phase:
            phase_lines = [line for line in lines if phase.lower() in line.lower()]
            handoff = self._parse_handoff_lines(phase_lines)
            if handoff is not None:
                return handoff

        return self._parse_handoff_lines(lines)

    @staticmethod
    def _extract_section(content: str, section: str) -> str:
        pattern = rf"(?ims)^##\s+{re.escape(section)}\s*\r?\n(?P<body>.*?)(?=^##\s+|\Z)"
        match = re.search(pattern, content)
        if not match:
            return ""
        return match.group("body").strip()

    @staticmethod
    def _parse_handoff_lines(lines: list[str]) -> str | None:
        for line in lines:
            match = re.search(r"Agent\s+(\d{2})", line, flags=re.IGNORECASE)
            if match:
                return match.group(1)

            normalized = line.lower()
            if "encerr" in normalized or "[end]" in normalized or "ultimo agente" in normalized:
                return ""
        return None

    def _ensure_handoff_packet(self, result: AgentResult) -> list[str]:
        if not isinstance(result.outputs, dict):
            return ["outputs_not_dict"]

        packet = result.outputs.get("handoff_packet")
        packet_payload = packet if isinstance(packet, dict) else {}

        normalized = {
            "from_agent_id": result.agent_id,
            "from_agent_name": result.agent_name,
            "from_stage": result.stage,
            "to_agent_id": result.handoff,
            "status": result.status,
            "summary": (
                str(packet_payload.get("summary", result.notes)).strip()
                if isinstance(packet_payload.get("summary", result.notes), str)
                else ""
            ),
            "artifacts": self._normalize_string_list(packet_payload.get("artifacts", result.artifacts)),
            "open_questions": self._normalize_string_list(packet_payload.get("open_questions", [])),
            "assumptions": self._normalize_string_list(packet_payload.get("assumptions", [])),
            "risks": self._normalize_string_list(packet_payload.get("risks", [])),
            "validation_snapshot": {
                "result_schema_ok": bool(result.checks.get("result_schema_ok")),
                "contract_loaded": bool(result.checks.get("contract_loaded")),
                "contract_required_sections_ok": bool(result.checks.get("contract_required_sections_ok")),
                "contract_handoff_match": bool(result.checks.get("contract_handoff_match")),
            },
            "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        result.outputs["handoff_packet"] = normalized

        missing_sections = [section for section in self._required_handoff_packet_sections if section not in normalized]
        errors = [f"missing_{section}" for section in missing_sections]

        if normalized["to_agent_id"] and not re.fullmatch(r"\d{2}", normalized["to_agent_id"]):
            errors.append("to_agent_id_invalid")
        if not normalized["summary"]:
            errors.append("summary_missing")
        if not isinstance(normalized["validation_snapshot"], dict):
            errors.append("validation_snapshot_invalid")
        if not isinstance(normalized["artifacts"], list):
            errors.append("artifacts_invalid")
        return errors

    def _stage_validation_requirements(self, result: AgentResult) -> dict[str, bool]:
        return {
            "result_schema_ok": bool(result.checks.get("result_schema_ok")),
            "contract_loaded": bool(result.checks.get("contract_loaded")),
            "contract_required_sections_ok": bool(result.checks.get("contract_required_sections_ok")),
            "contract_handoff_match": bool(result.checks.get("contract_handoff_match")),
            "handoff_packet_ok": bool(result.checks.get("handoff_packet_ok")),
            "notes_present": bool(result.checks.get("initial_notes_present")),
            "artifacts_exist": self._artifacts_exist(result.artifacts),
        }

    def _artifacts_exist(self, artifacts: list[str]) -> bool:
        if not isinstance(artifacts, list):
            return False
        for artifact in artifacts:
            if not isinstance(artifact, str) or not artifact.strip():
                return False
            path = Path(artifact)
            candidate = path if path.is_absolute() else self.repo_root / path
            if not candidate.exists():
                return False
        return True

    @staticmethod
    def _normalize_string_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if isinstance(item, str) and item.strip()]

    def _write(self, relative_path: str, content: str) -> str:
        target = self.repo_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content.strip() + "\n", encoding="utf-8")
        logger.info("Agent %s wrote %s", self.agent_id, relative_path)
        return str(target)

    def _append(self, relative_path: str, content: str) -> str:
        target = self.repo_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(content)
        logger.info("Agent %s appended to %s", self.agent_id, relative_path)
        return str(target)
