import pytest
from livekit.agents import AgentSession, mock_tools
from livekit.plugins import openai

from agent import Assistant, AppointmentAgent, SuggestionAgent, BusinessDevelopmentAgent


@pytest.mark.asyncio
async def test_assistant_greeting():
    """Test that Anna (receptionist) provides a friendly greeting and offers assistance."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        result = await session.run(user_input="Hello")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Makes a friendly introduction as a receptionist and offers assistance."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_assistant_appointment_handoff():
    """Test that Anna correctly hands off to appointment agent when user wants to schedule."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        result = await session.run(user_input="I need to schedule a plumbing appointment")
        
        # Should call the transfer function
        result.expect.next_event().is_function_call(name="transfer_to_appointment_agent")
        result.expect.next_event().is_function_call_output()
        
        # Should provide a message about transferring
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the appointment request and mentions connecting to a specialist."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_assistant_feedback_handoff():
    """Test that Anna correctly hands off to suggestion agent when user wants to provide feedback."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        result = await session.run(user_input="I want to complain about my recent service")
        
        # Should call the transfer function
        result.expect.next_event().is_function_call(name="transfer_to_suggestion_agent")
        result.expect.next_event().is_function_call_output()
        
        # Should provide a message about transferring
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the feedback request and mentions connecting to a specialist."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_assistant_business_handoff():
    """Test that Anna correctly hands off to business development agent for business inquiries."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        result = await session.run(user_input="I'm from another company and want to sell you services")
        
        # Should call the transfer function
        result.expect.next_event().is_function_call(name="transfer_to_business_development_agent")
        result.expect.next_event().is_function_call_output()
        
        # Should provide a message about transferring
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the business inquiry and mentions connecting to a specialist."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_appointment_agent_booking_flow():
    """Test that Naya (appointment agent) can handle a complete booking flow."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(AppointmentAgent())
        
        # First, user asks about scheduling
        result1 = await session.run(user_input="I need to schedule a plumbing repair")
        
        await result1.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Introduces herself as appointment specialist and asks for details."
        )
        result1.expect.no_more_events()
        
        # User provides details
        result2 = await session.run(user_input="My name is John Smith, I have a leaky faucet at 123 Main St, 90210")
        
        # Should ask for more details or check availability
        await result2.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the information and asks for more details or checks availability."
        )
        result2.expect.no_more_events()


@pytest.mark.asyncio
async def test_appointment_agent_checks_availability():
    """Test that Naya can check technician availability."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(AppointmentAgent())
        
        result = await session.run(user_input="What times are available for appointments?")
        
        # Should call the availability function
        result.expect.next_event().is_function_call(name="get_technician_available_times")
        result.expect.next_event().is_function_call_output()
        
        # Should provide available times
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Provides available appointment times from the function call result."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_suggestion_agent_feedback_collection():
    """Test that Helen (suggestion agent) can collect customer feedback."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(SuggestionAgent())
        
        result = await session.run(user_input="I want to provide feedback about my recent service")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Introduces herself as feedback specialist and asks about the feedback."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_business_development_agent_service_inquiry():
    """Test that Marcus (business development agent) handles service inquiries."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(BusinessDevelopmentAgent())
        
        result = await session.run(user_input="I want to sell marketing services to your plumbing company")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Introduces himself as business development specialist and asks for details about the service offering."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_business_development_agent_irrelevant_request():
    """Test that Marcus properly rejects irrelevant business requests."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(BusinessDevelopmentAgent())
        
        result = await session.run(user_input="I want to sell you pet grooming services")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Politely explains that the request doesn't align with the company's needs and declines to proceed."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_appointment_agent_books_appointment():
    """Test that Naya can book an appointment with proper details."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(AppointmentAgent())
        
        # Simulate a complete booking conversation
        result = await session.run(user_input="Book me for tomorrow at 2pm with John Smith")
        
        # Should call the booking function
        result.expect.next_event().is_function_call(name="book_appointment_in_db")
        result.expect.next_event().is_function_call_output()
        
        # Should provide confirmation
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Provides appointment confirmation with tracking ID."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_suggestion_agent_stores_feedback():
    """Test that Helen stores customer feedback properly."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(SuggestionAgent())
        
        result = await session.run(user_input="The technician was late and didn't fix the problem properly")
        
        # Should call the storage function
        result.expect.next_event().is_function_call(name="store_customer_suggestions")
        result.expect.next_event().is_function_call_output()
        
        # Should provide acknowledgment
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the feedback and thanks the customer for their input."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_business_development_agent_stores_request():
    """Test that Marcus stores business development requests."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(BusinessDevelopmentAgent())
        
        result = await session.run(user_input="I want to sell you accounting software for $500/month")
        
        # Should call the storage function
        result.expect.next_event().is_function_call(name="store_miscellaneous_requests_in_db")
        result.expect.next_event().is_function_call_output()
        
        # Should provide acknowledgment
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the business request and explains it will be reviewed."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_appointment_agent_cancels_appointment():
    """Test that Naya can cancel appointments."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(AppointmentAgent())
        
        result = await session.run(user_input="Cancel my appointment with tracking ID 123456")
        
        # Should call the cancellation function
        result.expect.next_event().is_function_call(name="cancel_appointments_by_tracking_ids")
        result.expect.next_event().is_function_call_output()
        
        # Should provide confirmation
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Confirms the appointment cancellation."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_appointment_agent_finds_existing_appointments():
    """Test that Naya can find existing appointments for a customer."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(AppointmentAgent())
        
        result = await session.run(user_input="What are my existing appointments?")
        
        # Should call the function to find appointments
        result.expect.next_event().is_function_call(name="find_active_appointments_for_customer")
        result.expect.next_event().is_function_call_output()
        
        # Should provide the appointment information
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Provides information about existing appointments."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_suggestion_agent_finds_past_appointments():
    """Test that Helen can find past appointments for feedback context."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(SuggestionAgent())
        
        result = await session.run(user_input="I want to give feedback about my appointment last week")
        
        # Should call the function to find past appointments
        result.expect.next_event().is_function_call(name="get_finished_appointments_for_customer")
        result.expect.next_event().is_function_call_output()
        
        # Should ask for clarification about which appointment
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Asks which specific appointment the feedback is about."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_multiple_turns_conversation():
    """Test a multi-turn conversation with context retention."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        # First turn - user greets
        result1 = await session.run(user_input="Hello")
        await result1.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Provides a friendly greeting and offers assistance."
        )
        result1.expect.no_more_events()
        
        # Second turn - user asks about appointments
        result2 = await session.run(user_input="I need to schedule an appointment")
        
        # Should call the transfer function
        result2.expect.next_event().is_function_call(name="transfer_to_appointment_agent")
        result2.expect.next_event().is_function_call_output()
        
        # Should provide transfer message
        await result2.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the appointment request and mentions connecting to a specialist."
        )
        result2.expect.no_more_events()


@pytest.mark.asyncio
async def test_agent_handles_emergency_mention():
    """Test that Anna properly handles emergency situations."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        result = await session.run(user_input="I have a burst pipe and water is flooding my basement!")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the emergency situation and offers immediate assistance or escalation."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_agent_handles_general_questions():
    """Test that Anna can answer general questions about plumbing services."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        result = await session.run(user_input="What services do you offer?")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Provides information about plumbing services offered by the company."
        )
        result.expect.no_more_events()
