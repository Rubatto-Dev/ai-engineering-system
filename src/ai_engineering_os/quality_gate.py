from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from .repository import required_doc_paths


def evaluate_quality_gate(
    repo_root: Path,
    tests_ok: bool = True,
    security_ok: bool = True,
    sonar_ok: bool | None = None,
) -> dict[str, object]:
    docs = required_doc_paths(repo_root)
    docs_ok = all(path.exists() and path.read_text(encoding="utf-8").strip() for path in docs)
    adr_ok = (repo_root / "docs" / "decisions" / "ADR-0001.md").exists()
    tooling = evaluate_tooling_setup(repo_root)

    sonar_signal = True if sonar_ok is None else sonar_ok
    sonar_gate_ok = tooling["sonarqube_ready"] and sonar_signal

    checks = {
        "tests_ok": tests_ok,
        "docs_updated": docs_ok,
        "security_checks_ok": security_ok,
        "quality_gate_ok": sonar_gate_ok,
        "adr_updated": adr_ok,
        "context7_configured": tooling["context7_ready"],
        "sequential_thinking_configured": tooling["sequential_thinking_ready"],
        "mcp_servers_configured": tooling["mcp_servers_ready"],
        "sonarqube_configured": tooling["sonarqube_ready"],
    }
    overall = all(checks.values())
    return {
        "ok": overall,
        "checks": checks,
        "tooling": tooling["details"],
    }


def evaluate_tooling_setup(repo_root: Path) -> dict[str, Any]:
    mcp_status = _read_mcp_status(repo_root / "config" / "mcp-servers.json")
    policy_status = _read_tooling_policy(repo_root / "config" / "tooling.yaml")
    sonar_status = _read_sonar_properties(repo_root / "sonar-project.properties")

    context7_ready = mcp_status["context7_server_ready"] and policy_status["context7_enabled"]
    sequential_ready = mcp_status["sequential_server_ready"] and policy_status["sequential_thinking_enabled"]
    mcp_servers_ready = mcp_status["context7_server_ready"] and mcp_status["sequential_server_ready"]
    sonarqube_ready = sonar_status["configured"] and policy_status["sonarqube_enabled"]

    return {
        "context7_ready": context7_ready,
        "sequential_thinking_ready": sequential_ready,
        "mcp_servers_ready": mcp_servers_ready,
        "sonarqube_ready": sonarqube_ready,
        "details": {
            "mcp": mcp_status,
            "tooling_policy": policy_status,
            "sonarqube": sonar_status,
        },
    }


def _read_mcp_status(path: Path) -> dict[str, Any]:
    base = {
        "file_present": path.exists(),
        "json_valid": False,
        "context7_server_ready": False,
        "sequential_server_ready": False,
    }
    if not path.exists():
        base["error"] = "mcp_servers_file_missing"
        return base

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        base["error"] = "mcp_servers_json_invalid"
        return base

    servers = payload.get("mcpServers", {})
    context7 = servers.get("context7", {})
    sequential = servers.get("sequential-thinking", {})

    base["json_valid"] = True
    base["context7_server_ready"] = _valid_server_definition(context7)
    base["sequential_server_ready"] = _valid_server_definition(sequential)
    return base


def _valid_server_definition(server: Any) -> bool:
    if not isinstance(server, dict):
        return False
    command = server.get("command")
    args = server.get("args")
    return isinstance(command, str) and bool(command.strip()) and isinstance(args, list) and bool(args)


def _read_tooling_policy(path: Path) -> dict[str, Any]:
    defaults = {
        "file_present": path.exists(),
        "context7_enabled": False,
        "sequential_thinking_enabled": False,
        "sonarqube_enabled": False,
    }
    if not path.exists():
        defaults["error"] = "tooling_policy_missing"
        return defaults

    enabled_flags = _extract_enabled_flags(path.read_text(encoding="utf-8-sig").splitlines())
    defaults["context7_enabled"] = enabled_flags.get("context7", False)
    defaults["sequential_thinking_enabled"] = enabled_flags.get("sequential_thinking", False)
    defaults["sonarqube_enabled"] = enabled_flags.get("sonarqube", False)
    return defaults


def _extract_enabled_flags(lines: list[str]) -> dict[str, bool]:
    in_integrations = False
    current_key: str | None = None
    flags: dict[str, bool] = {}

    integration_key = re.compile(r"^\s{2}([a-zA-Z0-9_-]+):\s*$")
    enabled_key = re.compile(r"^\s{4}enabled:\s*(true|false)\s*$", flags=re.IGNORECASE)

    for raw in lines:
        if not raw.strip():
            continue
        if raw.strip() == "integrations:":
            in_integrations = True
            continue
        if in_integrations and not raw.startswith(" "):
            break
        if not in_integrations:
            continue

        match_integration = integration_key.match(raw)
        if match_integration:
            current_key = match_integration.group(1)
            continue

        match_enabled = enabled_key.match(raw)
        if match_enabled and current_key:
            flags[current_key] = match_enabled.group(1).lower() == "true"

    return flags


def _read_sonar_properties(path: Path) -> dict[str, Any]:
    result = {
        "file_present": path.exists(),
        "configured": False,
        "missing_keys": [],
    }
    if not path.exists():
        result["missing_keys"] = ["sonar.projectKey", "sonar.sources", "sonar.tests"]
        result["error"] = "sonar_properties_missing"
        return result

    properties: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", maxsplit=1)
        properties[key.strip()] = value.strip()

    required_keys = ["sonar.projectKey", "sonar.sources", "sonar.tests"]
    missing = [key for key in required_keys if not properties.get(key)]
    result["missing_keys"] = missing
    result["configured"] = not missing
    return result
