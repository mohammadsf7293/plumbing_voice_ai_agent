"""Worker entrypoint. Business logic is also runnable without provider credentials."""
from livekit import agents
from livekit.agents import AgentSession, RoomInputOptions
from livekit.plugins import openai, deepgram, silero, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from plumbing.agents import (
    Assistant, AppointmentAgent, SuggestionAgent, BusinessDevelopmentAgent,
    transfer_to_appointment_agent, transfer_to_suggestion_agent,
    transfer_to_business_development_agent,
)
from plumbing.state import UserData
from plumbing.speech import clean_text
from plumbing.config import load_environment, validate_environment
from plumbing.telemetry import attach_session_events, emit
from plumbing.tools import get_technician_available_times_from_db


async def entrypoint(ctx: agents.JobContext):
    validate_environment()
    userdata = UserData()
    userdata.agents = {
        "anna": Assistant(), "naya": AppointmentAgent(),
        "helen": SuggestionAgent(), "marcus": BusinessDevelopmentAgent(),
    }
    session = AgentSession(
        userdata=userdata,
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=openai.LLM(model="gpt-4o-mini"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    attach_session_events(session, userdata.session_id)
    emit(userdata.session_id, "session_started")
    await session.start(
        room=ctx.room,
        agent=userdata.agents["anna"],
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVCTelephony()),
    )


if __name__ == "__main__":
    load_environment()
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
