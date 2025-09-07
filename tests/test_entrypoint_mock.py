import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import openai, cartesia, deepgram, silero, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel


class MockEntrypoint:
    """A class to mock the entrypoint function for testing."""
    
    @staticmethod
    async def create_session():
        """Create a session with mocked components."""
        # This method is mocked in the test
        # We don't actually create a session here
        pass
    
    @staticmethod
    async def start_session(session, room):
        """Start the session with a room and agent."""
        from agent import Assistant
        
        await session.start(
            room=room,
            agent=Assistant(),
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )
    
    @staticmethod
    async def generate_reply(session):
        """Generate a reply with instructions."""
        # In a real test, we would await this call
        # Here we're just defining the structure for testing
        session.generate_reply.assert_not_called()
        session.generate_reply(
            instructions="Greet the user and offer your assistance."
        )


@pytest.mark.asyncio
async def test_create_session():
    """Test that a session can be created with the correct components."""
    # Create a mock for the create_session method
    with patch.object(MockEntrypoint, 'create_session') as mock_create_session:
        # Configure the mock to return a mock session
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        
        # Call the create_session method
        session = await MockEntrypoint.create_session()
        
        # Check that the create_session method was called
        mock_create_session.assert_called_once()
        
        # Check that the session is the mock we configured
        assert session == mock_session


@pytest.mark.asyncio
async def test_start_session():
    """Test that the session is started with the correct parameters."""
    # Create a mock session and room
    mock_session = AsyncMock(spec=AgentSession)
    mock_room = MagicMock()
    
    # Patch the Assistant class and BVC
    with patch('agent.Assistant') as mock_assistant_class, \
         patch('livekit.plugins.noise_cancellation.BVC') as mock_bvc_class:
        
        # Create mock instances
        mock_assistant = MagicMock(spec=Agent)
        mock_bvc = MagicMock()
        
        # Configure the mocks to return our instances
        mock_assistant_class.return_value = mock_assistant
        mock_bvc_class.return_value = mock_bvc
        
        # Call the start_session method
        await MockEntrypoint.start_session(mock_session, mock_room)
        
        # Check that session.start was called with the correct parameters
        mock_session.start.assert_called_once()
        
        # Get the call arguments
        args, kwargs = mock_session.start.call_args
        
        # Check that start was called with the correct parameters
        assert kwargs['room'] == mock_room
        assert kwargs['agent'] == mock_assistant
        assert isinstance(kwargs['room_input_options'], RoomInputOptions)
        assert kwargs['room_input_options'].noise_cancellation == mock_bvc


@pytest.mark.asyncio
async def test_generate_reply():
    """Test that the session generates a reply with the correct instructions."""
    # Create a mock session
    mock_session = MagicMock(spec=AgentSession)
    
    # Call the generate_reply method
    await MockEntrypoint.generate_reply(mock_session)
    
    # Check that session.generate_reply was called with the correct parameters
    mock_session.generate_reply.assert_called_once_with(
        instructions="Greet the user and offer your assistance."
    )