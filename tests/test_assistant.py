import pytest
from livekit.agents import AgentSession
from livekit.plugins import openai

from agent import Assistant, get_technician_available_times_from_db, clean_text


@pytest.mark.asyncio
async def test_assistant_initialization():
    """Test that the Assistant class initializes correctly."""
    # Create an instance of the Assistant class
    assistant = Assistant()
    
    # Check that the instructions are set correctly
    # We'll just check that the instructions contain a specific phrase rather than the entire text
    assert "You are Anna, a helpful and friendly receptionist for a plumbing company." in assistant.instructions


@pytest.mark.asyncio
async def test_assistant_greeting_behavior():
    """Test that the Assistant provides appropriate greeting behavior."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        result = await session.run(user_input="Hello")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Provides a friendly greeting as Anna the receptionist and offers assistance."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_assistant_handoff_behavior():
    """Test that the Assistant correctly identifies when to hand off to specialists."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        # Test appointment handoff
        result = await session.run(user_input="I need to schedule a plumbing appointment")
        
        result.expect.next_event().is_function_call(name="transfer_to_appointment_agent")
        result.expect.next_event().is_function_call_output()
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges the appointment request and mentions connecting to a specialist."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_get_technician_available_times_from_db():
    """Test that the get_technician_available_times_from_db function returns the expected list."""
    # Call the function without a technician name
    result = await get_technician_available_times_from_db()
    
    # Check that the result is a list
    assert isinstance(result, list)
    
    # Check that the list contains the expected number of time slots
    assert len(result) > 0
    
    # Check that each item in the list is a string in CSV format
    for time_slot in result:
        assert isinstance(time_slot, str)
        # Check that each string contains a comma (CSV format)
        assert "," in time_slot
        # Split the string and check that it has a technician name and a time slot
        parts = time_slot.split(",", 1)
        assert len(parts) == 2
        assert parts[0]  # Technician name is not empty
        assert parts[1]  # Time slot is not empty


@pytest.mark.asyncio
async def test_get_technician_available_times_from_db_with_filter():
    """Test that the get_technician_available_times_from_db function correctly filters by technician name."""
    # Call the function with a specific technician name
    technician_name = "John Smith"
    result = await get_technician_available_times_from_db(technician_name)
    
    # Check that the result is a list
    assert isinstance(result, list)
    
    # Check that the list contains at least one time slot
    assert len(result) > 0
    
    # Check that all time slots are for the specified technician
    for time_slot in result:
        assert time_slot.startswith(f"{technician_name},")


@pytest.mark.asyncio
async def test_assistant_has_technician_times_tool():
    """Test that the Assistant has the get_technician_available_times tool registered."""
    # Create an instance of the Assistant class
    assistant = Assistant()
    
    # Check that the assistant has tools
    assert hasattr(assistant, 'tools')
    assert assistant.tools is not None
    
    # Check that there's at least one tool
    assert len(assistant.tools) > 0
    
    # Check that one of the tools is the get_technician_available_times tool
    # The tools might be wrapped in a way that doesn't expose a 'name' attribute directly
    # Instead, let's check if any tool's string representation contains our function name
    tool_found = False
    for tool in assistant.tools:
        if "get_technician_available_times" in str(tool):
            tool_found = True
            break
    assert tool_found, "get_technician_available_times tool not found in assistant tools"


def test_clean_text():
    """Test that the clean_text function correctly removes markdown characters."""
    # Test basic markdown symbols
    assert clean_text("**bold**") == "bold"
    assert clean_text("_italic_") == "italic"
    assert clean_text("# heading") == " heading"
    assert clean_text("`code`") == "code"
    assert clean_text("~strikethrough~") == "strikethrough"
    assert clean_text("> quote") == " quote"
    assert clean_text("- list item") == " list item"
    
    # Test multiple symbols
    assert clean_text("**_bold italic_**") == "bold italic"
    assert clean_text("# `code heading`") == " code heading"
    
    # Test symbols in middle of text
    assert clean_text("This is *bold* text") == "This is bold text"
    assert clean_text("Before-after") == "Beforeafter"
    
    # Test empty string
    assert clean_text("") == ""
    
    # Test string with only symbols
    assert clean_text("*_#`~>-") == ""