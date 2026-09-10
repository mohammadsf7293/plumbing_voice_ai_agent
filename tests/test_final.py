import pytest
from livekit.agents import AgentSession
from livekit.plugins import openai

from agent import Assistant, AppointmentAgent, SuggestionAgent, BusinessDevelopmentAgent, UserData


@pytest.mark.provider
@pytest.mark.asyncio
async def test_assistant_greeting():
    """Test that Anna provides a friendly greeting."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=Assistant())
        
        result = await session.run(user_input="Hello")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Provides a friendly greeting as Anna the receptionist and offers assistance."
        )
        result.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_appointment_agent_greeting():
    """Test that Naya provides appropriate greeting."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=AppointmentAgent())
        
        result = await session.run(user_input="Hello")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Introduces herself as Naya the appointment specialist and offers to help with appointments."
        )
        result.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_suggestion_agent_greeting():
    """Test that Helen provides appropriate greeting."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=SuggestionAgent())
        
        result = await session.run(user_input="Hello")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Introduces herself as Helen the customer feedback specialist and offers assistance."
        )
        result.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_business_development_agent_greeting():
    """Test that Marcus provides appropriate greeting."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=BusinessDevelopmentAgent())
        
        result = await session.run(user_input="Hello")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Introduces himself as Marcus the business development specialist and offers to help with business inquiries."
        )
        result.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_assistant_responds_to_appointment_request():
    """Test that Anna responds appropriately to appointment requests."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=Assistant())
        
        result = await session.run(user_input="I need to schedule a plumbing appointment")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the appointment request and offers to help or connect with a specialist."
        )
        result.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_assistant_responds_to_feedback_request():
    """Test that Anna responds appropriately to feedback requests."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=Assistant())
        
        result = await session.run(user_input="I want to complain about my service")
        
        # Just check that Anna acknowledges the feedback - handoffs may or may not happen in test context
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the feedback request and offers to help or connect with a specialist."
        )
        
        # Don't check for more events - handoffs are complex in test context
        # The important thing is that Anna responds appropriately


@pytest.mark.provider
@pytest.mark.asyncio
async def test_assistant_responds_to_business_inquiry():
    """Test that Anna responds appropriately to business inquiries."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=Assistant())
        
        result = await session.run(user_input="I want to sell you services")
        
        # Just check that Anna acknowledges the business inquiry - handoffs may or may not happen in test context
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the business inquiry and offers to help or connect with a specialist."
        )
        
        # Don't check for more events - handoffs are complex in test context
        # The important thing is that Anna responds appropriately


@pytest.mark.provider
@pytest.mark.asyncio
async def test_appointment_agent_responds_to_booking_request():
    """Test that Naya responds appropriately to booking requests."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=AppointmentAgent())
        
        result = await session.run(user_input="I need to book an appointment for tomorrow")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the booking request and asks for necessary information to proceed with the appointment."
        )
        result.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_suggestion_agent_responds_to_feedback():
    """Test that Helen responds appropriately to feedback."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=SuggestionAgent())
        
        result = await session.run(user_input="I had a bad experience with your service")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the feedback and asks for more details about the experience."
        )
        result.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_business_development_agent_responds_to_service_inquiry():
    """Test that Marcus responds appropriately to service inquiries."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=BusinessDevelopmentAgent())
        
        result = await session.run(user_input="I want to sell you marketing services")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the service inquiry and asks for more details about the marketing services."
        )
        result.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_multiple_turns_conversation():
    """Test a multi-turn conversation with context retention."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=Assistant())
        
        # First turn - user greets
        result1 = await session.run(user_input="Hello")
        await result1.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Provides a friendly greeting and offers assistance."
        )
        result1.expect.no_more_events()
        
        # Second turn - user asks about appointments
        result2 = await session.run(user_input="I need to schedule an appointment")
        
        await result2.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the appointment request and asks for more details about the plumbing issue."
        )
        result2.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_agent_handles_emergency_mention():
    """Test that Anna properly handles emergency situations."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=Assistant())
        
        result = await session.run(user_input="I have a burst pipe and water is flooding my basement!")
        
        # Just check that Anna acknowledges the emergency - handoffs may or may not happen in test context
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the emergency situation and offers immediate assistance or escalation."
        )
        
        # Don't check for more events - handoffs are complex in test context
        # The important thing is that Anna responds appropriately to emergencies


@pytest.mark.provider
@pytest.mark.asyncio
async def test_agent_handles_general_questions():
    """Test that Anna can answer general questions about plumbing services."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=Assistant())
        
        result = await session.run(user_input="What services do you offer?")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Provides information about plumbing services offered by the company."
        )
        result.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_agent_handles_unclear_requests():
    """Test that Anna handles unclear or ambiguous requests."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=Assistant())
        
        result = await session.run(user_input="I need help with something")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Offers assistance and asks how they can help the user."
        )
        result.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_agent_handles_off_topic_requests():
    """Test that Anna handles off-topic requests appropriately."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=Assistant())
        
        result = await session.run(user_input="What's the weather like today?")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Politely explains they cannot help with weather and asks if there's anything else they can help with."
        )
        result.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_agent_handles_booking_flow():
    """Test that the appointment agent can handle a basic booking flow."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=AppointmentAgent())
        
        # First request
        result1 = await session.run(user_input="I need to book an appointment")
        await result1.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the booking request and asks for necessary information."
        )
        result1.expect.no_more_events()
        
        # Follow-up with details
        result2 = await session.run(user_input="My name is John Smith and I have a leaky faucet")
        await result2.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the information provided and continues gathering details for the appointment."
        )
        result2.expect.no_more_events()


@pytest.mark.provider
@pytest.mark.asyncio
async def test_agent_handles_feedback_flow():
    """Test that the suggestion agent can handle a basic feedback flow."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create userdata to avoid context errors
        userdata = UserData()
        session.userdata = userdata
        
        await session.start(agent=SuggestionAgent())
        
        # First request
        result1 = await session.run(user_input="I want to give feedback about my service")
        await result1.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the feedback request and asks for more details."
        )
        result1.expect.no_more_events()
        
        # Follow-up with details
        result2 = await session.run(user_input="The technician was late and didn't fix the problem")
        await result2.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the specific feedback and asks for more details or offers to help."
        )
        result2.expect.no_more_events()
