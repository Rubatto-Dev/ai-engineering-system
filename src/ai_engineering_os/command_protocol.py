from __future__ import annotations

from dataclasses import dataclass
import re


class ProtocolError(ValueError):
    """Raised when a JARVIS command is invalid."""


@dataclass(frozen=True)
class JarvisCommand:
    name: str
    args: dict[str, str]


_ALLOWED = {"START", "PLAN", "EXEC", "AUDIT", "SHIP"}
_REQUIRED = {
    "START": {"project"},
    "PLAN": {"cycle"},
    "EXEC": {"cycle", "mode"},
    "AUDIT": set(),
    "SHIP": {"version"},
}
_ALLOWED_MODES = {"advisor", "builder", "autopilot_safe", "autopilot_full", "audit"}
_TOKEN_RE = re.compile(r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[^\s]+)")


def parse_command(raw: str) -> JarvisCommand:
    text = raw.strip()
    prefix = "JARVIS:"
    if not text.upper().startswith(prefix):
        raise ProtocolError("Command must start with 'JARVIS:'")

    body = text[len(prefix) :].strip()
    if not body:
        raise ProtocolError("Missing command name")

    parts = body.split(maxsplit=1)
    name = parts[0].upper()
    if name not in _ALLOWED:
        raise ProtocolError(f"Unsupported command: {name}")

    args_text = parts[1] if len(parts) > 1 else ""
    args: dict[str, str] = {}
    for match in _TOKEN_RE.finditer(args_text):
        args[match.group("key")] = match.group("value")

    _validate(name, args)
    return JarvisCommand(name=name, args=args)


def _validate(name: str, args: dict[str, str]) -> None:
    missing = _REQUIRED[name] - set(args)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ProtocolError(f"Missing required argument(s): {missing_text}")

    if "cycle" in args:
        if not args["cycle"].isdigit() or int(args["cycle"]) <= 0:
            raise ProtocolError("cycle must be a positive integer")

    if name == "EXEC":
        mode = args.get("mode", "")
        if mode not in _ALLOWED_MODES:
            raise ProtocolError(f"Unsupported mode: {mode}")
