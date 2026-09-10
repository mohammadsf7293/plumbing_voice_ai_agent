"""Exercise the real entrypoint, mocking only provider/model boundaries."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
import agent


async def test_entrypoint_wires_session_and_room(monkeypatch):
    session = Mock()
    session.start = AsyncMock()
    session_factory = Mock(return_value=session)
    monkeypatch.setattr(agent, "AgentSession", session_factory)
    for name, target in (("LLM", agent.openai), ("STT", agent.deepgram)):
        monkeypatch.setattr(target, name, Mock())
    monkeypatch.setattr(agent.silero.VAD, "load", Mock())
    monkeypatch.setattr(agent, "MultilingualModel", Mock())
    monkeypatch.setattr(agent.noise_cancellation, "BVCTelephony", Mock())
    room = object()
    await agent.entrypoint(SimpleNamespace(room=room))
    userdata = session_factory.call_args.kwargs['userdata']
    assert set(userdata.agents) == {"anna", "naya", "helen", "marcus"}
    assert session.start.await_args.kwargs['room'] is room
    assert session.start.await_args.kwargs['agent'] is userdata.agents['anna']
    assert session.start.await_args.kwargs['room_input_options'].noise_cancellation is agent.noise_cancellation.BVCTelephony.return_value
    assert {c.args[0] for c in session.on.call_args_list} == {"metrics_collected", "function_tools_executed", "agent_state_changed", "error"}
    agent.deepgram.STT.assert_called_once_with(model="nova-3", language="en")
    agent.openai.LLM.assert_called_once_with(model="gpt-4o-mini")
