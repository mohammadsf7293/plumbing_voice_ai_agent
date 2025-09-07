import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from livekit.agents import AgentSession, Agent, RoomInputOptions, JobContext
from livekit.plugins import openai, cartesia, deepgram, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel


@pytest.fixture(autouse=True)
def mock_job_context_var():
    """Mock the job context variable to avoid RuntimeError in tests."""
    with patch('livekit.agents.job.get_job_context') as mock_get_job_context:
        # Create a mock job context with an inference executor
        mock_context = MagicMock(spec=JobContext)
        mock_context.inference_executor = MagicMock()
        mock_get_job_context.return_value = mock_context
        yield mock_context


@pytest.fixture
def mock_room():
    """Mock LiveKit Room object."""
    room = MagicMock()
    room.name = "test-room"
    return room


@pytest.fixture
def mock_job_context(mock_room):
    """Mock JobContext with a mock room."""
    context = MagicMock(spec=JobContext)
    context.room = mock_room
    return context


@pytest.fixture
def mock_openai_llm():
    """Mock OpenAI LLM."""
    llm = AsyncMock(spec=openai.LLM)
    llm.generate_response = AsyncMock(return_value="This is a mock response")
    return llm


@pytest.fixture
def mock_deepgram_stt():
    """Mock Deepgram STT."""
    stt = AsyncMock(spec=deepgram.STT)
    stt.transcribe = AsyncMock(return_value="This is a mock transcription")
    return stt


@pytest.fixture
def mock_cartesia_tts():
    """Mock Cartesia TTS."""
    tts = AsyncMock(spec=cartesia.TTS)
    tts.synthesize = AsyncMock(return_value=b"mock audio data")
    return tts


@pytest.fixture
def mock_silero_vad():
    """Mock Silero VAD."""
    vad = AsyncMock(spec=silero.VAD)
    return vad


@pytest.fixture
def mock_turn_detection():
    """Mock turn detection."""
    turn_detection = AsyncMock(spec=MultilingualModel)
    return turn_detection


@pytest.fixture
def mock_agent_session(mock_openai_llm, mock_deepgram_stt, mock_cartesia_tts, mock_silero_vad, mock_turn_detection):
    """Mock AgentSession with mocked components."""
    session = AsyncMock(spec=AgentSession)
    session.llm = mock_openai_llm
    session.stt = mock_deepgram_stt
    session.tts = mock_cartesia_tts
    session.vad = mock_silero_vad
    session.turn_detection = mock_turn_detection
    session.start = AsyncMock()
    session.generate_reply = AsyncMock()
    session.run = AsyncMock()
    
    # Create a mock result that can be used in tests
    mock_result = AsyncMock()
    mock_result.expect = AsyncMock()
    mock_result.expect.next_event = AsyncMock(return_value=mock_result)
    mock_result.is_message = AsyncMock(return_value=mock_result)
    session.run.return_value = mock_result
    
    return session


@pytest.fixture
def mock_agent_session_factory(mock_agent_session):
    """Factory fixture to create a mock AgentSession."""
    with patch('livekit.agents.AgentSession', return_value=mock_agent_session):
        yield