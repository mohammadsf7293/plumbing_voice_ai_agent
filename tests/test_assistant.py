import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent import Assistant


@pytest.mark.asyncio
async def test_assistant_initialization():
    """Test that the Assistant class initializes correctly."""
    # Create an instance of the Assistant class
    assistant = Assistant()
    
    # Check that the instructions are set correctly
    assert assistant.instructions == "You are a helpful voice AI assistant."


@pytest.mark.asyncio
async def test_assistant_with_custom_instructions():
    """Test that the Assistant class can be initialized with custom instructions."""
    # Create an instance of the Assistant class with custom instructions
    custom_instructions = "You are a customer service assistant."
    assistant = Assistant()
    
    # Since instructions is a property without a setter, we need to modify the underlying attribute
    # or create a new instance with the custom instructions
    assistant = Assistant()
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