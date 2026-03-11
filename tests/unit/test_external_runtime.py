from __future__ import annotations

from http.client import RemoteDisconnected

import pytest

import ai_engineering_os.external_runtime as runtime_module


@pytest.mark.unit
def test_probe_sonar_api_handles_remote_disconnect(monkeypatch: pytest.MonkeyPatch) -> None:
    def _broken_urlopen(*_args: object, **_kwargs: object) -> object:
        raise RemoteDisconnected("Remote end closed connection without response")

    monkeypatch.setattr(runtime_module.request, "urlopen", _broken_urlopen)

    result = runtime_module._probe_sonar_api()

    assert result["ok"] is False
    assert result["url"].endswith("/api/system/status")
    assert "Remote end closed connection without response" in str(result.get("error", ""))
