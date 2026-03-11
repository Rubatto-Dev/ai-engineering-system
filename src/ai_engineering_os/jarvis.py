from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from .command_protocol import JarvisCommand, parse_command
from .external_runtime import evaluate_runtime_readiness
from .pipeline import EngineeringPipeline
from .proposal_profile import build_proposal_profile, load_proposal_text
from .quality_gate import evaluate_quality_gate
from .repository import ensure_structure


class JarvisEngine:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        ensure_structure(self.repo_root)
        self.current_project: str | None = None
        self.pipeline = EngineeringPipeline(self.repo_root)

        self.last_exec_result: dict[str, Any] | None = None
        self.last_audit_result: dict[str, Any] | None = None
        self.current_proposal_file: str | None = None
        self.current_proposal_text: str | None = None
        self.current_proposal_profile: dict[str, Any] | None = None
        self._exec_counter = 0
        self._last_exec_counter: int | None = None
        self._audited_exec_counter: int | None = None

    def handle(self, raw_command: str) -> dict[str, object]:
        command = parse_command(raw_command)
        if command.name == "START":
            return self._start(command)
        if command.name == "PLAN":
            return self._plan(command)
        if command.name == "EXEC":
            return self._exec(command)
        if command.name == "AUDIT":
            return self._audit(command)
        if command.name == "SHIP":
            return self._ship(command)
        raise ValueError(f"Unhandled command: {command.name}")

    def _start(self, command: JarvisCommand) -> dict[str, object]:
        self.current_project = command.args["project"]
        self.last_exec_result = None
        self.last_audit_result = None
        self.current_proposal_file = None
        self.current_proposal_text = None
        self.current_proposal_profile = None
        self._exec_counter = 0
        self._last_exec_counter = None
        self._audited_exec_counter = None

        proposal_arg = command.args.get("proposal_file")
        proposal_path, proposal_text = load_proposal_text(self.repo_root, proposal_arg)
        profile = build_proposal_profile(self.current_project, proposal_text)
        self.current_proposal_file = proposal_path
        self.current_proposal_text = proposal_text
        self.current_proposal_profile = profile

        proposal_notice = "sem arquivo de proposta"
        if proposal_arg:
            proposal_notice = f"arquivo solicitado: {proposal_arg}"
        if proposal_path:
            proposal_notice = f"proposta carregada: {proposal_path}"

        (self.repo_root / "docs" / "01_visao.md").write_text(
            "\n".join(
                [
                    "# Visao",
                    "",
                    f"Projeto iniciado: {self.current_project}",
                    f"Tipo inferido: {profile['project_type']}",
                    f"Feasibility: {profile['feasibility']}",
                    f"Estimativa (semanas): {profile['estimated_duration_weeks']['min']} - {profile['estimated_duration_weeks']['max']}",
                    f"Observacao de proposta: {proposal_notice}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return {
            "status": "started",
            "project": self.current_project,
            "protocol": "jarvis_command_protocol",
            "context7": "enabled",
            "sequential_thinking": "enabled",
            "proposal_loaded": bool(proposal_path),
            "proposal_file": proposal_path,
            "proposal_profile": profile,
        }

    def _plan(self, command: JarvisCommand) -> dict[str, object]:
        self._require_project()
        cycle = int(command.args["cycle"])
        steps = self.pipeline.plan_steps()
        return {
            "status": "planned",
            "project": self.current_project,
            "cycle": cycle,
            "steps": steps,
            "agents_expected": 15,
        }

    def _exec(self, command: JarvisCommand) -> dict[str, object]:
        self._require_project()
        cycle = int(command.args["cycle"])
        mode = command.args["mode"]
        result = self.pipeline.run(
            project=self.current_project or "unknown",
            cycle=cycle,
            mode=mode,
            proposal_profile=self.current_proposal_profile,
            proposal_text=self.current_proposal_text,
            proposal_file=self.current_proposal_file,
        )
        self.last_exec_result = result
        self.last_audit_result = None
        self._exec_counter += 1
        self._last_exec_counter = self._exec_counter
        self._audited_exec_counter = None
        return result

    def _audit(self, command: JarvisCommand) -> dict[str, object]:
        tests_ok = _as_bool(command.args["tests_ok"]) if "tests_ok" in command.args else self._default_tests_ok()
        security_ok = (
            _as_bool(command.args["security_ok"]) if "security_ok" in command.args else self._default_security_ok()
        )
        sonar_ok = _as_bool(command.args["sonar_ok"]) if "sonar_ok" in command.args else None
        strict_external = _as_bool(command.args["strict_external"]) if "strict_external" in command.args else False

        gate = evaluate_quality_gate(
            self.repo_root,
            tests_ok=tests_ok,
            security_ok=security_ok,
            sonar_ok=sonar_ok,
        )
        external_runtime: dict[str, Any] | None = None
        if strict_external:
            external_runtime = evaluate_runtime_readiness(self.repo_root)
            gate["checks"]["external_runtime_ok"] = external_runtime["ok"]
            gate["ok"] = bool(gate["ok"]) and bool(external_runtime["ok"])

        result: dict[str, object] = {
            "status": "audit_ok" if gate["ok"] else "audit_failed",
            "result": gate,
            "inputs": {
                "tests_ok": tests_ok,
                "security_ok": security_ok,
                "sonar_ok": sonar_ok,
                "strict_external": strict_external,
            },
            "external_runtime": external_runtime,
        }
        self.last_audit_result = result
        self._audited_exec_counter = self._last_exec_counter
        return result

    def _ship(self, command: JarvisCommand) -> dict[str, object]:
        self._require_project()
        if self._last_exec_counter is None:
            return {
                "status": "ship_blocked",
                "reason": "execution_required",
            }
        if self.last_audit_result is None or self._audited_exec_counter != self._last_exec_counter:
            return {
                "status": "ship_blocked",
                "reason": "audit_required",
            }
        if self.last_audit_result.get("status") != "audit_ok":
            return {
                "status": "ship_blocked",
                "reason": "audit_failed",
                "result": self.last_audit_result.get("result"),
            }

        checks = self.last_audit_result["result"]["checks"]  # type: ignore[index]
        gate = evaluate_quality_gate(
            self.repo_root,
            tests_ok=bool(checks.get("tests_ok")),
            security_ok=bool(checks.get("security_checks_ok")),
            sonar_ok=bool(checks.get("quality_gate_ok")),
        )
        if not gate["ok"]:
            return {
                "status": "ship_blocked",
                "reason": "quality_gate_changed_after_audit",
                "result": gate,
            }

        version = command.args["version"]
        notes_path = self.repo_root / "docs" / "16_release_notes.md"
        with notes_path.open("a", encoding="utf-8") as handle:
            handle.write(f"\n## Release {version} - {date.today().isoformat()}\n")
            handle.write("- Ship gate passed\n")
            handle.write("- SonarQube: ok\n")
            handle.write("- Security checks: ok\n")

        return {
            "status": "shipped",
            "project": self.current_project,
            "version": version,
            "release_notes": str(notes_path),
        }

    def _default_tests_ok(self) -> bool:
        if not self.last_exec_result:
            return False
        return self.last_exec_result.get("status") == "success"

    def _default_security_ok(self) -> bool:
        if not self.last_exec_result:
            return False
        stages = self.last_exec_result.get("stages", [])
        if not isinstance(stages, list):
            return False
        for stage in stages:
            if not isinstance(stage, dict):
                continue
            if stage.get("agent_id") == "13":
                checks = stage.get("checks", {})
                if isinstance(checks, dict):
                    return bool(checks.get("security_ok"))
        return False

    def _require_project(self) -> None:
        if not self.current_project:
            raise RuntimeError("Project not started. Run JARVIS: START project=<name> first.")


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "ok"}
