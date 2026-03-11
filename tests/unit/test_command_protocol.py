from __future__ import annotations

import pytest

from ai_engineering_os.command_protocol import ProtocolError, parse_command


@pytest.mark.unit
def test_parse_start_command() -> None:
    cmd = parse_command("JARVIS: START project=alpha")
    assert cmd.name == "START"
    assert cmd.args["project"] == "alpha"


@pytest.mark.unit
def test_parse_exec_command() -> None:
    cmd = parse_command("JARVIS: EXEC cycle=2 mode=autopilot_safe")
    assert cmd.name == "EXEC"
    assert cmd.args["cycle"] == "2"
    assert cmd.args["mode"] == "autopilot_safe"


@pytest.mark.unit
def test_parse_missing_required_arg() -> None:
    with pytest.raises(ProtocolError):
        parse_command("JARVIS: START")


@pytest.mark.unit
def test_parse_invalid_mode() -> None:
    with pytest.raises(ProtocolError):
        parse_command("JARVIS: EXEC cycle=1 mode=invalid")
