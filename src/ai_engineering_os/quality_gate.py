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
        "decision_policy_configured": tooling["decision_policy_ready"],
        "stage_validation_policy_configured": tooling["stage_validation_policy_ready"],
        "communication_protocol_configured": tooling["communication_protocol_ready"],
        "agent_training_configured": tooling["agent_training_ready"],
        "npm_scripts_cross_platform": tooling["npm_scripts_cross_platform_ready"],
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
    decision_policy_status = _read_decision_policy_config(repo_root / "config" / "decision_policy.json")
    stage_validation_policy_status = _read_stage_validation_policy(repo_root / "config" / "stage_validation.json")
    communication_protocol_status = _read_communication_protocol(repo_root / "protocol" / "AGENT_COMMUNICATION_PROTOCOL.md")
    agent_training_status = _read_agent_training_config(repo_root / "config" / "agent_training.json")
    npm_scripts_status = _read_npm_scripts_config(repo_root / "package.json")

    context7_ready = mcp_status["context7_server_ready"] and policy_status["context7_enabled"]
    sequential_ready = mcp_status["sequential_server_ready"] and policy_status["sequential_thinking_enabled"]
    mcp_servers_ready = mcp_status["context7_server_ready"] and mcp_status["sequential_server_ready"]
    sonarqube_ready = sonar_status["configured"] and policy_status["sonarqube_enabled"]
    decision_policy_ready = decision_policy_status["configured"]
    stage_validation_policy_ready = stage_validation_policy_status["configured"]
    communication_protocol_ready = communication_protocol_status["configured"]
    agent_training_ready = agent_training_status["configured"]
    npm_scripts_cross_platform_ready = npm_scripts_status["configured"]

    return {
        "context7_ready": context7_ready,
        "sequential_thinking_ready": sequential_ready,
        "mcp_servers_ready": mcp_servers_ready,
        "sonarqube_ready": sonarqube_ready,
        "decision_policy_ready": decision_policy_ready,
        "stage_validation_policy_ready": stage_validation_policy_ready,
        "communication_protocol_ready": communication_protocol_ready,
        "agent_training_ready": agent_training_ready,
        "npm_scripts_cross_platform_ready": npm_scripts_cross_platform_ready,
        "details": {
            "mcp": mcp_status,
            "tooling_policy": policy_status,
            "sonarqube": sonar_status,
            "decision_policy": decision_policy_status,
            "stage_validation_policy": stage_validation_policy_status,
            "communication_protocol": communication_protocol_status,
            "agent_training": agent_training_status,
            "npm_scripts": npm_scripts_status,
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


def _read_decision_policy_config(path: Path) -> dict[str, Any]:
    result = {
        "file_present": path.exists(),
        "configured": False,
        "missing_keys": [],
    }
    if not path.exists():
        result["missing_keys"] = ["version", "thresholds", "labels", "segment_thresholds", "calibration"]
        result["error"] = "decision_policy_missing"
        return result

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        result["error"] = "decision_policy_json_invalid"
        return result

    if not isinstance(payload, dict):
        result["error"] = "decision_policy_invalid_shape"
        return result

    missing: list[str] = []
    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        missing.append("version")

    thresholds = payload.get("thresholds")
    required_thresholds = [
        "go_min_score",
        "go_with_caveats_min_score",
        "go_max_ambiguity_score",
        "go_max_open_gaps",
        "no_go_max_score",
        "no_go_min_open_gaps",
        "no_go_min_ambiguity_score",
    ]
    if not isinstance(thresholds, dict):
        missing.append("thresholds")
    else:
        for key in required_thresholds:
            if key not in thresholds:
                missing.append(f"thresholds.{key}")

    labels = payload.get("labels")
    required_labels = ["go", "go_with_caveats", "no_go"]
    if not isinstance(labels, dict):
        missing.append("labels")
    else:
        for key in required_labels:
            value = labels.get(key)
            if not isinstance(value, str) or not value.strip():
                missing.append(f"labels.{key}")

    segment_thresholds = payload.get("segment_thresholds")
    required_segments = ["frontend", "backend", "automacao", "fullstack"]
    if not isinstance(segment_thresholds, dict):
        missing.append("segment_thresholds")
    else:
        for segment in required_segments:
            segment_payload = segment_thresholds.get(segment)
            if not isinstance(segment_payload, dict):
                missing.append(f"segment_thresholds.{segment}")
                continue
            segment_threshold_values = segment_payload.get("thresholds", segment_payload)
            if not isinstance(segment_threshold_values, dict):
                missing.append(f"segment_thresholds.{segment}.thresholds")
                continue
            for key in required_thresholds:
                if key not in segment_threshold_values:
                    missing.append(f"segment_thresholds.{segment}.thresholds.{key}")

    calibration = payload.get("calibration")
    if not isinstance(calibration, dict):
        missing.append("calibration")
    else:
        min_samples = calibration.get("min_samples_per_segment")
        history_file = calibration.get("history_file")
        window_days = calibration.get("window_days")
        min_score_spread = calibration.get("min_score_spread")
        min_ambiguity_spread = calibration.get("min_ambiguity_spread")
        if min_samples is None:
            missing.append("calibration.min_samples_per_segment")
        if not isinstance(history_file, str) or not history_file.strip():
            missing.append("calibration.history_file")
        if window_days is None:
            missing.append("calibration.window_days")
        if min_score_spread is None:
            missing.append("calibration.min_score_spread")
        if min_ambiguity_spread is None:
            missing.append("calibration.min_ambiguity_spread")

    result["missing_keys"] = missing
    result["configured"] = not missing
    return result


def _read_stage_validation_policy(path: Path) -> dict[str, Any]:
    result = {
        "file_present": path.exists(),
        "configured": False,
        "missing_keys": [],
    }
    if not path.exists():
        result["missing_keys"] = [
            "version",
            "require_stage_validation_ok",
            "require_handoff_packet",
            "require_contract_loaded",
            "require_notes_present",
            "require_artifacts_exist",
            "block_on_any_missing",
        ]
        result["error"] = "stage_validation_policy_missing"
        return result

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        result["error"] = "stage_validation_policy_json_invalid"
        return result

    if not isinstance(payload, dict):
        result["error"] = "stage_validation_policy_invalid_shape"
        return result

    missing: list[str] = []
    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        missing.append("version")

    required_flags = [
        "require_stage_validation_ok",
        "require_handoff_packet",
        "require_contract_loaded",
        "require_notes_present",
        "require_artifacts_exist",
        "block_on_any_missing",
    ]
    for key in required_flags:
        if not isinstance(payload.get(key), bool):
            missing.append(key)

    result["missing_keys"] = missing
    result["configured"] = not missing
    return result


def _read_communication_protocol(path: Path) -> dict[str, Any]:
    result = {
        "file_present": path.exists(),
        "configured": False,
        "missing_sections": [],
        "missing_terms": [],
    }
    if not path.exists():
        result["missing_sections"] = ["Communication Contract", "Handoff Rules", "Validation Snapshot"]
        result["missing_terms"] = ["handoff_packet", "validation_snapshot"]
        result["error"] = "communication_protocol_missing"
        return result

    content = path.read_text(encoding="utf-8-sig")
    sections = ["Communication Contract", "Handoff Rules", "Validation Snapshot"]
    missing_sections = [
        section for section in sections if not re.search(rf"(?im)^##\s+{re.escape(section)}\s*$", content)
    ]

    lowered = content.lower()
    required_terms = ["handoff_packet", "validation_snapshot", "to_agent_id"]
    missing_terms = [term for term in required_terms if term not in lowered]

    result["missing_sections"] = missing_sections
    result["missing_terms"] = missing_terms
    result["configured"] = not missing_sections and not missing_terms
    return result


def _read_agent_training_config(path: Path) -> dict[str, Any]:
    result = {
        "file_present": path.exists(),
        "configured": False,
        "missing_keys": [],
    }
    if not path.exists():
        result["missing_keys"] = [
            "version",
            "history_file",
            "leaderboard_file",
            "weights",
            "thresholds",
            "leaderboard",
            "shadow_mode",
        ]
        result["error"] = "agent_training_policy_missing"
        return result

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        result["error"] = "agent_training_policy_json_invalid"
        return result

    if not isinstance(payload, dict):
        result["error"] = "agent_training_policy_invalid_shape"
        return result

    missing: list[str] = []
    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        missing.append("version")

    for key in ["history_file", "leaderboard_file", "shadow_report_file"]:
        value = payload.get(key)
        if key == "shadow_report_file" and value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            missing.append(key)

    weights = payload.get("weights")
    if not isinstance(weights, dict):
        missing.append("weights")
    else:
        for key in ["execution_success", "stage_validation", "handoff_quality", "audit_success", "artifact_coverage"]:
            if key not in weights:
                missing.append(f"weights.{key}")

    thresholds = payload.get("thresholds")
    if not isinstance(thresholds, dict):
        missing.append("thresholds")
    else:
        for key in ["promotion_score", "watch_score", "min_runs_for_promotion"]:
            if key not in thresholds:
                missing.append(f"thresholds.{key}")

    leaderboard = payload.get("leaderboard")
    if not isinstance(leaderboard, dict):
        missing.append("leaderboard")
    else:
        for key in ["window_days", "min_runs"]:
            if key not in leaderboard:
                missing.append(f"leaderboard.{key}")

    shadow_mode = payload.get("shadow_mode")
    if not isinstance(shadow_mode, dict):
        missing.append("shadow_mode")
    else:
        for key in ["enabled", "mode", "profile"]:
            if key not in shadow_mode:
                missing.append(f"shadow_mode.{key}")

    result["missing_keys"] = missing
    result["configured"] = not missing
    return result


def _read_npm_scripts_config(path: Path) -> dict[str, Any]:
    result = {
        "file_present": path.exists(),
        "configured": False,
        "missing_scripts": [],
        "non_portable_scripts": [],
    }
    if not path.exists():
        result["missing_scripts"] = [
            "test:python",
            "quality:python",
            "runtime:check",
            "audit:safety",
            "policy:calibrate",
            "agents:leaderboard",
            "sonar:up",
            "sonar:down",
        ]
        result["error"] = "package_json_missing"
        return result

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        result["error"] = "package_json_invalid"
        return result

    if not isinstance(payload, dict):
        result["error"] = "package_json_invalid_shape"
        return result

    scripts = payload.get("scripts")
    if not isinstance(scripts, dict):
        result["error"] = "package_scripts_missing"
        return result

    required_scripts = [
        "test:python",
        "quality:python",
        "runtime:check",
        "audit:safety",
        "policy:calibrate",
        "agents:leaderboard",
        "sonar:up",
        "sonar:down",
    ]
    missing_scripts = [key for key in required_scripts if not isinstance(scripts.get(key), str) or not scripts.get(key)]
    result["missing_scripts"] = missing_scripts

    non_portable: list[str] = []
    for key in required_scripts:
        command = scripts.get(key)
        if not isinstance(command, str):
            continue
        normalized = command.lower()
        if ".cmd" in normalized or "\\" in command:
            non_portable.append(key)
    result["non_portable_scripts"] = non_portable
    result["configured"] = not missing_scripts and not non_portable
    return result
