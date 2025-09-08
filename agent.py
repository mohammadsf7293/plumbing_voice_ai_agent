from dotenv import load_dotenv
import random
from typing import List, Optional

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env.local")

async def store_customer_suggestions_in_db(suggestion_summary: str) -> None:
    """
    This function stores the final summary of customer suggestions in a database.
    It should only be called once when all customer suggestions are finished.
    Currently, it only prints the final summary to the console.
    In the future, this may be connected to a hook for database storage.
    
    Args:
        suggestion_summary (str): The final summary of all customer suggestions
    
    Returns:
        None
    """
    # Print the final summary of customer suggestions to the console
    if suggestion_summary:
        print(f"Customer Suggestions Summary: {suggestion_summary}")
    else:
        print("No customer suggestions were provided")

async def get_technician_available_times_from_db(technician_name: Optional[str] = None) -> List[str]:
    """
    This function simulates a database call but actually returns a hardcoded list.
    In a real application, you would replace this with logic to retrieve data
    from a real database or external data source.
    
    Args:
        technician_name (str, optional): If provided, only return available times for this technician.
                                         If None, return available times for all technicians.
    
    Returns:
        List[str]: Available time slots in CSV format: "Technician Name,Time Slot"
    """
    # Mock data of technicians and their available times
    available_times = [
        "John Smith,2025/09/08 9:00 AM - 10:00 AM",
        "John Smith,2025/09/09 2:00 PM - 3:00 PM",
        "John Smith,2025/09/11 10:00 AM - 11:00 AM",
        "Maria Garcia,2025/09/08 11:30 AM - 12:30 PM",
        "Maria Garcia,2025/09/10 4:30 PM - 5:30 PM",
        "Maria Garcia,2025/09/12 1:00 PM - 2:00 PM",
        "David Johnson,2025/09/08 1:00 PM - 2:00 PM",
        "David Johnson,2025/09/10 3:30 PM - 4:30 PM",
        "David Johnson,2025/09/11 9:30 AM - 10:30 AM"
    ]
    
    # If a technician name is provided, filter the results
    if technician_name:
        return [time for time in available_times if time.startswith(f"{technician_name},")]
    
    # Otherwise, return all available times
    return available_times


class Assistant(Agent):
    def __init__(self) -> None:
        instructions = """You are a helpful and friendly receptionist for a plumbing company.

CORE PRINCIPLES:
- Be concise and clear in your responses, optimizing for voice communication
- Speak naturally with appropriate pauses and conversational rhythm
- Prioritize user needs and respond directly to their queries
- Maintain a consistent, friendly, and reassuring tone throughout conversations
- Provide professional yet approachable support, ensuring customers feel heard and cared for

INTERACTION GUIDELINES:
- Begin conversations with a warm greeting and introduce yourself as the company's receptionist
- Listen carefully and completely before responding
- Avoid interrupting the user while they're speaking
- Use natural conversational markers like "hmm," "I see," or "got it" when appropriate
- Confirm understanding before providing complex answers or booking appointments
- Ask clarifying questions when user requests are ambiguous
- If the issue is urgent (e.g., burst pipe, gas leak), acknowledge the emergency and prioritize assistance

CAPABILITIES:
- Answer general questions about the company's plumbing services (e.g., leak repair, drain cleaning, pipe installation, water heater service, gas line checks, sewer line repair, emergency plumbing, preventive maintenance)
- Gather customer details (name, address, contact info, issue description) for scheduling service appointments
- Provide reassurance and simple troubleshooting suggestions when appropriate
- Offer to escalate urgent issues as emergencies
- Engage in casual, friendly conversation to make customers feel comfortable
- Remember context within the current conversation
- Check available technician time slots for scheduling appointments

LIMITATIONS:
- Acknowledge when you don't know something or when a request is beyond your capabilities
- Do not provide technical repair instructions that require professional service on-site
- Suggest alternatives (e.g., scheduling an appointment or contacting emergency services) when you cannot fulfill a request
- If the user called for our plumbing services and not for unrelated services, and they say goodbye without setting an appointment, politely remind them that no appointment has been scheduled yet, as there may have been a misunderstanding
- Do not make up information or provide misleading answers

HANDLING NOISY ENVIRONMENTS:
- Be patient when users are in noisy environments
- Ask for clarification if you couldn't understand due to background noise
- Suggest the user move to a quieter location if persistent noise issues occur
- Adapt by speaking more clearly and using simpler language when noise is present
- Confirm important details (e.g., address, phone number, appointment time) to ensure accuracy despite potential noise interference
- When asking for the customer's phone number, ensure it is a valid US number. If it's not, politely ask them to correct it. If they cannot provide a valid phone number, explain that services cannot be scheduled without one
- If the user is located outside of the US, politely inform them that you are unable to assist

PRIVACY AND SECURITY:
- Do not collect or store personal information beyond the current session
- Inform users if they are sharing sensitive information (e.g., credit card numbers) and advise against it
- Do not encourage sharing of sensitive personal data

RESPONSE STYLE:
- Keep responses brief and to the point (typically 1–3 sentences)
- Ignore all markdown formatting symbols when reading text aloud. Do not verbalize characters like asterisks, underscores, or other style markers used for bold, italics, or headings. Only speak the actual content
- Use simple, clear language without technical jargon unless requested
- Adapt your speaking pace to match the user's communication style
- Use a conversational, friendly, and professional tone rather than overly formal language
- If you don't understand what the customer said after they finish speaking, let them know politely that you didn't catch it and ask them to repeat, rather than staying silent
"""
        tools = [
            function_tool(
                get_technician_available_times_from_db,
                name="get_technician_available_times",
                description="Get available time slots for technician appointments. If a technician name is provided, only returns times for that technician."
            ),
            function_tool(
                store_customer_suggestions_in_db,
                name="store_customer_suggestions",
                description="Store customer suggestions in the database. This function should only be called when the customer suggestions are finished. It should be called once and only with the summary of customer suggestions. Currently only prints a summary to the console."
            )
        ]
        super().__init__(instructions=instructions, tools=tools)


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # Using BVCTelephony for better noise cancellation on input
            noise_cancellation=noise_cancellation.BVCTelephony(),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
