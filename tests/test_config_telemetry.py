import json
import logging
import socket
from types import SimpleNamespace
import pytest
from livekit.agents import AgentSession
from livekit.agents.voice.events import MetricsCollectedEvent, FunctionToolsExecutedEvent
from livekit.agents.metrics import LLMMetrics
from livekit.agents.llm import FunctionCall, FunctionCallOutput
from plumbing.config import validate_environment
from plumbing.telemetry import attach_session_events


def test_missing_configuration_reports_names_only(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY')
    with pytest.raises(ValueError, match='OPENAI_API_KEY') as error:
        validate_environment()
    assert 'offline-placeholder' not in str(error.value)


@pytest.mark.parametrize('url', ['https://example.com', 'wss://', 'example.com'])
def test_invalid_url(monkeypatch, url):
    monkeypatch.setenv('LIVEKIT_URL', url)
    with pytest.raises(ValueError, match='LIVEKIT_URL'):
        validate_environment()


def test_valid_environment():
    validate_environment()


def test_network_is_blocked():
    with socket.socket() as connection, pytest.raises(AssertionError, match='Network access'):
        connection.connect(('127.0.0.1', 9))


async def test_real_session_events_are_correlated_and_redacted(caplog):
    session = AgentSession()
    attach_session_events(session, 'test-session')
    caplog.set_level(logging.INFO, logger='plumbing.events')
    session.emit('metrics_collected', MetricsCollectedEvent(metrics=LLMMetrics(
        request_id='request-1', label='openai', timestamp=1, duration=.3, ttft=.1, cancelled=False,
        completion_tokens=5, prompt_tokens=10, prompt_cached_tokens=0, total_tokens=15, tokens_per_second=16.7,
    )))
    session.emit('function_tools_executed', FunctionToolsExecutedEvent(
        function_calls=[FunctionCall(call_id='call-1', name='book_appointment_in_db', arguments='{"phone":"private-data"}')],
        function_call_outputs=[FunctionCallOutput(call_id='call-1', name='book_appointment_in_db', output='private-data', is_error=True)],
    ))
    session.emit('error', SimpleNamespace(source=object(), error=ValueError('private-data')))
    events = [json.loads(record.message) for record in caplog.records]
    assert all(event['session_id'] == 'test-session' for event in events)
    assert events[0]['ttft'] == .1
    assert events[1]['status'] == 'error'
    assert events[2]['error_type'] == 'ValueError'
    assert 'private-data' not in caplog.text
    await session.aclose()
