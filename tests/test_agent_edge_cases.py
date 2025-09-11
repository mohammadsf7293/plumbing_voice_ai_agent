import pytest
from livekit.agents import AgentSession, mock_tools
from livekit.plugins import openai

from agent import Assistant, AppointmentAgent, SuggestionAgent, BusinessDevelopmentAgent


@pytest.mark.asyncio
async def test_appointment_agent_handles_booking_error():
    """Test that Naya handles booking errors gracefully."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Mock the booking function to raise an error
        with mock_tools(
            AppointmentAgent,
            {"book_appointment_in_db": lambda: RuntimeError("Database connection failed")},
        ):
            await session.start(AppointmentAgent())
            
            result = await session.run(user_input="Book me an appointment for tomorrow")
            
            # Should call the booking function
            result.expect.next_event().is_function_call(name="book_appointment_in_db")
            result.expect.next_event().is_function_call_output()
            
            # Should handle the error gracefully
            await result.expect.next_event().is_message(role="assistant").judge(
                llm, intent="Acknowledges the error and offers alternative solutions or asks to try again."
            )
            result.expect.no_more_events()


@pytest.mark.asyncio
async def test_appointment_agent_handles_no_availability():
    """Test that Naya handles no available time slots."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Mock the availability function to return empty list
        with mock_tools(
            AppointmentAgent,
            {"get_technician_available_times": lambda: []},
        ):
            await session.start(AppointmentAgent())
            
            result = await session.run(user_input="What times are available?")
            
            # Should call the availability function
            result.expect.next_event().is_function_call(name="get_technician_available_times")
            result.expect.next_event().is_function_call_output()
            
            # Should handle no availability gracefully
            await result.expect.next_event().is_message(role="assistant").judge(
                llm, intent="Informs the user that no time slots are currently available and offers alternatives."
            )
            result.expect.no_more_events()


@pytest.mark.asyncio
async def test_suggestion_agent_handles_storage_error():
    """Test that Helen handles feedback storage errors gracefully."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Mock the storage function to raise an error
        with mock_tools(
            SuggestionAgent,
            {"store_customer_suggestions": lambda: RuntimeError("Storage service unavailable")},
        ):
            await session.start(SuggestionAgent())
            
            result = await session.run(user_input="I want to complain about poor service")
            
            # Should call the storage function
            result.expect.next_event().is_function_call(name="store_customer_suggestions")
            result.expect.next_event().is_function_call_output()
            
            # Should handle the error gracefully
            await result.expect.next_event().is_message(role="assistant").judge(
                llm, intent="Acknowledges the error and assures the customer their feedback is still valued."
            )
            result.expect.no_more_events()


@pytest.mark.asyncio
async def test_business_development_agent_handles_storage_error():
    """Test that Marcus handles business request storage errors gracefully."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Mock the storage function to raise an error
        with mock_tools(
            BusinessDevelopmentAgent,
            {"store_miscellaneous_requests_in_db": lambda: RuntimeError("Database error")},
        ):
            await session.start(BusinessDevelopmentAgent())
            
            result = await session.run(user_input="I want to sell you marketing services")
            
            # Should call the storage function
            result.expect.next_event().is_function_call(name="store_miscellaneous_requests_in_db")
            result.expect.next_event().is_function_call_output()
            
            # Should handle the error gracefully
            await result.expect.next_event().is_message(role="assistant").judge(
                llm, intent="Acknowledges the error but assures the requester their information was received."
            )
            result.expect.no_more_events()


@pytest.mark.asyncio
async def test_appointment_agent_handles_invalid_tracking_id():
    """Test that Naya handles invalid tracking IDs for cancellation."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(AppointmentAgent())
        
        result = await session.run(user_input="Cancel my appointment with tracking ID abc123")
        
        # Should call the cancellation function
        result.expect.next_event().is_function_call(name="cancel_appointments_by_tracking_ids")
        result.expect.next_event().is_function_call_output()
        
        # Should handle invalid ID gracefully
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the cancellation request and provides appropriate response."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_assistant_handles_unclear_requests():
    """Test that Anna handles unclear or ambiguous requests."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        result = await session.run(user_input="I need help with something")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Asks clarifying questions to better understand what the user needs help with."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_assistant_handles_off_topic_requests():
    """Test that Anna handles off-topic requests appropriately."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        result = await session.run(user_input="What's the weather like today?")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Politely redirects the conversation back to plumbing services or offers to help with plumbing-related needs."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_appointment_agent_handles_missing_information():
    """Test that Naya asks for missing required information."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(AppointmentAgent())
        
        result = await session.run(user_input="I need an appointment")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Asks for required information like name, address, contact details, and problem description."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_suggestion_agent_handles_empty_feedback():
    """Test that Helen handles empty or vague feedback."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(SuggestionAgent())
        
        result = await session.run(user_input="I have feedback")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Asks for more specific details about the feedback or suggestions."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_business_development_agent_handles_incomplete_information():
    """Test that Marcus asks for complete business information."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(BusinessDevelopmentAgent())
        
        result = await session.run(user_input="I want to sell you something")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Asks for specific details about the service, contact information, and other required details."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_appointment_agent_handles_invalid_address():
    """Test that Naya validates US addresses."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(AppointmentAgent())
        
        result = await session.run(user_input="My address is 123 Main St, London, UK")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Informs the user that services are only available in the United States and asks for a US address."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_appointment_agent_handles_invalid_phone():
    """Test that Naya validates US phone number format."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(AppointmentAgent())
        
        result = await session.run(user_input="My phone number is 123-456")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Asks for a valid US phone number format."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_appointment_agent_handles_invalid_zip():
    """Test that Naya validates US zip code format."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(AppointmentAgent())
        
        result = await session.run(user_input="My zip code is ABC123")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Asks for a valid US zip code format."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_agent_handles_rapid_fire_requests():
    """Test that agents handle multiple rapid requests appropriately."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        # First request
        result1 = await session.run(user_input="Hello")
        await result1.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Provides a greeting and offers assistance."
        )
        result1.expect.no_more_events()
        
        # Second request immediately after
        result2 = await session.run(user_input="I need an appointment")
        result2.expect.next_event().is_function_call(name="transfer_to_appointment_agent")
        result2.expect.next_event().is_function_call_output()
        await result2.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the appointment request and mentions connecting to a specialist."
        )
        result2.expect.no_more_events()
        
        # Third request
        result3 = await session.run(user_input="Actually, I want to complain")
        result3.expect.next_event().is_function_call(name="transfer_to_suggestion_agent")
        result3.expect.next_event().is_function_call_output()
        await result3.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the feedback request and mentions connecting to a specialist."
        )
        result3.expect.no_more_events()
