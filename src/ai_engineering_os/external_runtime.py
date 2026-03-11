from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any
from urllib import error, request


def evaluate_runtime_readiness(repo_root: Path, startup_timeout: float = 3.0) -> dict[str, Any]:
    node_probe = _probe_command(["node", "--version"], repo_root, timeout=3.0)
    npm_probe = _probe_command([_npm_cmd_name(), "--version"], repo_root, timeout=3.0)

    mcp_config = _read_mcp_config(repo_root / "config" / "mcp-servers.json")
    context7_probe = _probe_mcp_server(mcp_config, "context7", repo_root, startup_timeout)
    sequential_probe = _probe_mcp_server(mcp_config, "sequential-thinking", repo_root, startup_timeout)

    sonar_probe = _probe_sonar_api()

    checks = {
        "node_available": node_probe["ok"],
        "npm_available": npm_probe["ok"],
        "context7_runtime_ready": context7_probe["ok"],
        "sequential_thinking_runtime_ready": sequential_probe["ok"],
        "sonar_api_reachable": sonar_probe["ok"],
    }

    return {
        "ok": all(checks.values()),
        "checks": checks,
        "details": {
            "node": node_probe,
            "npm": npm_probe,
            "mcp_config": mcp_config,
            "context7": context7_probe,
            "sequential_thinking": sequential_probe,
            "sonarqube": sonar_probe,
        },
    }


def _probe_mcp_server(
    mcp_config: dict[str, Any],
    server_name: str,
    repo_root: Path,
    timeout: float,
) -> dict[str, Any]:
    servers = mcp_config.get("mcpServers", {})
    server = servers.get(server_name)
    if not isinstance(server, dict):
        return {"ok": False, "error": f"missing_server_config:{server_name}"}

    command = server.get("command")
    args = server.get("args", [])
    if not isinstance(command, str) or not command.strip() or not isinstance(args, list) or not args:
        return {"ok": False, "error": f"invalid_server_config:{server_name}"}

    normalized_command = _normalize_node_command(command)
    return _probe_command([normalized_command, *[str(item) for item in args]], repo_root, timeout=timeout)


def _read_mcp_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"mcpServers": {}, "error": "config_missing"}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {"mcpServers": {}, "error": "config_invalid_json"}


def _probe_sonar_api() -> dict[str, Any]:
    host = os.getenv("SONAR_HOST_URL", "http://localhost:9000").rstrip("/")
    url = f"{host}/api/system/status"
    try:
        with request.urlopen(url, timeout=3.0) as response:
            payload = response.read(2048).decode("utf-8", errors="replace")
            system_status: str | None = None
            try:
                system_status = json.loads(payload).get("status")
            except json.JSONDecodeError:
                system_status = None
            status_ready = system_status in {"UP", "GREEN"}
            return {
                "ok": (200 <= response.status < 300) and status_ready,
                "status_code": response.status,
                "url": url,
                "system_status": system_status,
                "body_snippet": payload[:200],
            }
    except error.URLError as exc:
        return {"ok": False, "url": url, "error": str(exc)}
    except TimeoutError:
        return {"ok": False, "url": url, "error": "timeout"}
    except Exception as exc:  # pragma: no cover - defensive path for transient HTTP stack failures
        message = str(exc).strip() or exc.__class__.__name__
        return {"ok": False, "url": url, "error": message}


def _probe_command(command: list[str], cwd: Path, timeout: float) -> dict[str, Any]:
    executable = shutil.which(command[0])
    if not executable:
        return {"ok": False, "command": command, "error": "command_not_found"}

    try:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as exc:
        return {"ok": False, "command": command, "error": str(exc)}

    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return {
            "ok": process.returncode == 0,
            "command": command,
            "mode": "exited",
            "exit_code": process.returncode,
            "stdout": (stdout or "")[:200],
            "stderr": (stderr or "")[:200],
        }
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            process.kill()
        return {
            "ok": True,
            "command": command,
            "mode": "running_after_timeout",
            "exit_code": None,
            "stdout": "",
            "stderr": "",
        }


def _normalize_node_command(command: str) -> str:
    lowered = command.lower()
    if lowered == "npx":
        return _npx_cmd_name()
    if lowered == "npm":
        return _npm_cmd_name()
    return command


def _npm_cmd_name() -> str:
    return "npm.cmd" if os.name == "nt" else "npm"


def _npx_cmd_name() -> str:
    return "npx.cmd" if os.name == "nt" else "npx"
