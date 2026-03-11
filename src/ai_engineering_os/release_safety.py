from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
from typing import Any

from .external_runtime import evaluate_runtime_readiness
from .jarvis import JarvisEngine
from .quality_gate import evaluate_quality_gate


def run_release_safety_audit(repo_root: Path) -> dict[str, Any]:
    tests = _run_pytest(repo_root)
    quality = evaluate_quality_gate(repo_root, tests_ok=tests["ok"])
    runtime = evaluate_runtime_readiness(repo_root)

    sonar_runtime_ok = bool(runtime.get("checks", {}).get("sonar_api_reachable"))
    engine = JarvisEngine(repo_root)
    strict_audit = engine.handle(
        " ".join(
            [
                f"JARVIS: AUDIT repo={repo_root.name}",
                f"tests_ok={'true' if tests['ok'] else 'false'}",
                "security_ok=true",
                f"sonar_ok={'true' if sonar_runtime_ok else 'false'}",
                "strict_external=true",
            ]
        )
    )

    strict_ok = strict_audit.get("status") == "audit_ok"
    overall_ok = bool(tests["ok"]) and bool(quality["ok"]) and bool(runtime["ok"]) and strict_ok

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "ok": overall_ok,
        "checks": {
            "tests_ok": bool(tests["ok"]),
            "quality_ok": bool(quality["ok"]),
            "runtime_ok": bool(runtime["ok"]),
            "strict_audit_ok": strict_ok,
        },
        "details": {
            "tests": tests,
            "quality": quality,
            "runtime": runtime,
            "strict_audit": strict_audit,
        },
    }


def _run_pytest(repo_root: Path) -> dict[str, Any]:
    completed = subprocess.run(  # nosec - controlled local command
        [sys.executable, "-m", "pytest", "-q"],
        cwd=str(repo_root),
        check=False,
        capture_output=True,
        text=True,
    )
    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()
    return {
        "ok": completed.returncode == 0,
        "command": [sys.executable, "-m", "pytest", "-q"],
        "exit_code": completed.returncode,
        "stdout_tail": _tail(stdout),
        "stderr_tail": _tail(stderr),
    }


def _tail(text: str, max_lines: int = 20) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])
