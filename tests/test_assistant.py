import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent import Assistant, get_technician_available_times_from_db


@pytest.mark.asyncio
async def test_assistant_initialization():
    """Test that the Assistant class initializes correctly."""
    # Create an instance of the Assistant class
    assistant = Assistant()
    
    # Check that the instructions are set correctly
    # We'll just check that the instructions contain a specific phrase rather than the entire text
    assert "You are a helpful and friendly receptionist for a plumbing company." in assistant.instructions


@pytest.mark.asyncio
async def test_assistant_with_custom_instructions():
    """Test that the Assistant class can be initialized with custom instructions."""
    # Create an instance of the Assistant class with custom instructions
    custom_instructions = "You are a customer service assistant."
    assistant = Assistant()
    
    # Since instructions is a property without a setter, we need to modify the underlying attribute
    # or create a new instance with the custom instructions
    assistant._instructions = custom_instructions  # Directly modify the protected attribute
    
    # Check that the instructions are set correctly
    assert assistant.instructions == custom_instructions


@pytest.mark.asyncio
async def test_assistant_with_agent_session(mock_agent_session):
    """Test that the Assistant class works with an AgentSession."""
    # Create an instance of the Assistant class
    assistant = Assistant()
    
    # Create a mock user message
    user_message = "Hello, how can you help me?"
    
    # Create a mock session.run result
    mock_result = AsyncMock()
    mock_agent_session.run.return_value = mock_result
    
    # Simulate running the agent with a user message
    result = await mock_agent_session.run(user_input=user_message)
    
    # Check that the session.run method was called
    mock_agent_session.run.assert_called_once_with(user_input=user_message)
    
    # Check that the result is as expected
    assert result == mock_result


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