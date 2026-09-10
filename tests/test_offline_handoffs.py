from types import SimpleNamespace
from unittest.mock import AsyncMock, PropertyMock, patch
import pytest
from livekit.agents import Agent
from plumbing.agents import (
    Assistant, AppointmentAgent, SuggestionAgent, BusinessDevelopmentAgent,
    transfer_to_appointment_agent, transfer_to_suggestion_agent, transfer_to_business_development_agent,
)
from plumbing.state import UserData


@pytest.mark.parametrize('transfer,kind,name', [
    (transfer_to_appointment_agent, AppointmentAgent, 'naya'),
    (transfer_to_suggestion_agent, SuggestionAgent, 'helen'),
    (transfer_to_business_development_agent, BusinessDevelopmentAgent, 'marcus'),
])
async def test_handoff_summary_reaches_entry_greeting_and_clears(transfer, kind, name):
    previous = Assistant()
    session = SimpleNamespace(userdata=UserData(), current_agent=previous, generate_reply=AsyncMock())
    context = SimpleNamespace(userdata=session.userdata, session=session)
    destination = await transfer(context, 'kitchen sink leak')
    assert isinstance(destination, kind)
    assert session.userdata.prev_agent is previous
    assert session.userdata.agents[name] is destination
    with patch.object(Agent, 'session', new_callable=PropertyMock, return_value=session):
        await destination.on_enter()
        assert 'kitchen sink leak' in session.generate_reply.call_args.kwargs['instructions']
        assert await transfer(context) is destination
        await destination.on_enter()
        assert 'kitchen sink leak' not in session.generate_reply.call_args.kwargs['instructions']
        assert session.userdata.problem_description is None


async def test_receptionist_entry_requests_greeting():
    session = SimpleNamespace(generate_reply=AsyncMock())
    with patch.object(Agent, 'session', new_callable=PropertyMock, return_value=session):
        await Assistant().on_enter()
    session.generate_reply.assert_awaited_once()
    assert 'Greet' in session.generate_reply.call_args.kwargs['instructions']
