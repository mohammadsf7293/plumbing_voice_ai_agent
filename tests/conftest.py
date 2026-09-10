"""Offline by default. Provider calls require an explicit --run-provider flag."""
import socket
import pytest


def pytest_addoption(parser):
    parser.addoption("--run-provider", action="store_true", help="Allow paid provider-backed evaluations")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-provider"):
        for item in items:
            if "provider" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="Requires credentials and --run-provider; not verified offline"))


@pytest.fixture(autouse=True)
def offline_guard(request, monkeypatch):
    if "provider" in request.keywords and request.config.getoption("--run-provider"):
        from plumbing.config import load_environment
        load_environment()
        return
    # No real credentials are read by offline tests, even on a configured laptop.
    for key in ("OPENAI_API_KEY", "CARTESIA_API_KEY", "DEEPGRAM_API_KEY", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"):
        monkeypatch.setenv(key, "offline-placeholder")
    monkeypatch.setenv("LIVEKIT_URL", "wss://offline.invalid")
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")

    def blocked(*args, **kwargs):
        raise AssertionError("Network access is disabled in offline tests")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
