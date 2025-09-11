from dotenv import load_dotenv
import random
from random import randint
from typing import List, Optional, Dict, Literal
from enum import Enum
from dataclasses import dataclass, field

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool, RunContext
import re
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env.local")

def clean_text(text: str) -> str:
    """Remove markdown symbols from text before TTS processing.
    
    Args:
        text (str): The text containing markdown symbols
        
    Returns:
        str: Clean text with markdown symbols removed
    """
    return re.sub(r'[*_#`~>-]', '', text)
class CleanTTS(cartesia.TTS):
    """TTS class that cleans markdown symbols from text before processing"""
    
    async def say(self, text: str, **kwargs: any) -> None:
        """Clean markdown symbols from text before TTS processing
        
        Args:
            text (str): The text to speak
            **kwargs: Additional arguments passed to parent say method
        """
        clean = clean_text(text)
        await super().say(clean, **kwargs)

# Use a single voice ID for all agents to avoid TTS errors
voices = {
    "receptionist": "6f84f4b8-58a2-430c-8c79-688dad597532",
    "appointment_specialist": "156fb8d2-335b-4950-9cb3-a2d33befec77",
    "suggestions_receptionist": "794f9389-aac1-45b6-b726-9d9369183238",
    "business_development": "39b376fc-488e-4d0c-8b37-e00b72059fdd",
}

# Request type enum
class RequestType(str, Enum):
    SELLING_SERVICES = "SELLING_SERVICES"
    EMPLOYMENT_REQUEST = "EMPLOYMENT_REQUEST"
    OTHER = "OTHER"

@dataclass
class UserData:
    """User data that persists across agent handoffs"""
    # Store the previous agent to maintain context
    prev_agent: Optional[Agent] = None
    # Dictionary to store agents by name
    agents: Dict[str, Agent] = field(default_factory=dict)
    # Store problem description for context passing
    problem_description: Optional[str] = None

async def cancel_appointments_by_tracking_ids(tracking_ids: List[int]) -> str:
    """
    Cancels appointments with the given tracking IDs.
    
    Args:
        tracking_ids (List[int]): List of 6-digit tracking IDs for appointments to cancel
    
    Returns:
        str: Confirmation message
    """
    # Print cancellation information to the console
    if tracking_ids:
        print(f"APPOINTMENTS CANCELLED - Tracking IDs: {', '.join(map(str, tracking_ids))}")
        
        # In a real application, this would update a database to mark these appointments as cancelled
        
        # Return confirmation message
        if len(tracking_ids) == 1:
            return f"Your appointment with tracking ID {tracking_ids[0]} has been cancelled."
        else:
            return f"Your appointments with tracking IDs {', '.join(map(str, tracking_ids))} have been cancelled."
    else:
        return "No tracking IDs provided for cancellation."

async def get_finished_appointments_for_customer(customer_name: str) -> List[str]:
    """
    Finds all past/completed appointments for a given customer.
    
    Args:
        customer_name (str): The name of the customer to find appointments for
    
    Returns:
        List[str]: List of past appointments in format "Tracking ID,Technician Name,Time Slot"
    """
    # This is a mock implementation that generates random past appointments
    # In a real application, this would query a database
    
    # Generate a random number of appointments (0-3)
    num_appointments = random.randint(0, 3)
    
    if num_appointments == 0:
        return []
    
    # List of technicians
    technicians = ["John Smith", "Maria Garcia", "David Johnson"]
    
    # Generate random appointments
    appointments = []
    for _ in range(num_appointments):
        # Generate a random 6-digit tracking ID
        tracking_id = str(randint(100000, 999999))
        
        # Select a random technician
        technician = random.choice(technicians)
        
        # Generate a random date in the past 30 days
        days_ago = random.randint(1, 30)
        appointment_date = f"2025/08/{8 + days_ago}"
        
        # Generate a random time
        hour = random.randint(9, 16)
        minute = random.choice([0, 30])
        end_hour = hour + 1
        
        # Format the time slot
        if hour < 12:
            time_slot = f"{appointment_date} {hour}:{minute:02d} AM - {end_hour}:{minute:02d} AM"
        elif hour == 12:
            time_slot = f"{appointment_date} {hour}:{minute:02d} PM - {end_hour}:{minute:02d} PM"
        else:
            time_slot = f"{appointment_date} {hour-12}:{minute:02d} PM - {end_hour-12}:{minute:02d} PM"
        
        # Create the appointment string
        appointment = f"{tracking_id},{technician},{time_slot}"
        appointments.append(appointment)
    
    return appointments

async def find_active_appointments_for_customer(customer_name: str) -> List[str]:
    """
    Finds all active appointments for a given customer.
    
    Args:
        customer_name (str): The name of the customer to find appointments for
    
    Returns:
        List[str]: List of active appointments in format "Tracking ID,Technician Name,Time Slot"
    """
    # This is a mock implementation that generates random appointments
    # In a real application, this would query a database
    
    # Generate a random number of appointments (0-3)
    num_appointments = random.randint(0, 3)
    
    if num_appointments == 0:
        return []
    
    # List of technicians
    technicians = ["John Smith", "Maria Garcia", "David Johnson"]
    
    # Generate random appointments
    appointments = []
    for _ in range(num_appointments):
        # Generate a random 6-digit tracking ID
        tracking_id = str(randint(100000, 999999))
        
        # Select a random technician
        technician = random.choice(technicians)
        
        # Generate a random date in the next 14 days
        days_ahead = random.randint(1, 14)
        appointment_date = f"2025/09/{8 + days_ahead}"
        
        # Generate a random time
        hour = random.randint(9, 16)
        minute = random.choice([0, 30])
        end_hour = hour + 1
        
        # Format the time slot
        if hour < 12:
            time_slot = f"{appointment_date} {hour}:{minute:02d} AM - {end_hour}:{minute:02d} AM"
        elif hour == 12:
            time_slot = f"{appointment_date} {hour}:{minute:02d} PM - {end_hour}:{minute:02d} PM"
        else:
            time_slot = f"{appointment_date} {hour-12}:{minute:02d} PM - {end_hour-12}:{minute:02d} PM"
        
        # Create the appointment string
        appointment = f"{tracking_id},{technician},{time_slot}"
        appointments.append(appointment)
    
    return appointments

async def book_appointment_in_db(customer_name: str, agent_name: str, timeslot: str) -> str:
    """
    Books an appointment in the database and generates a tracking ID.
    
    Args:
        customer_name (str): The name of the customer
        agent_name (str): The name of the agent handling the booking
        timeslot (str): The selected appointment timeslot
    
    Returns:
        str: Confirmation message with appointment tracking ID
    """
    # Generate a random 6-digit appointment ID
    appointment_id = randint(100000, 999999)
    
    # Print confirmation to logs
    print(f"APPOINTMENT CONFIRMED - ID: {appointment_id}")
    print(f"Customer: {customer_name}")
    print(f"Agent: {agent_name}")
    print(f"Timeslot: {timeslot}")
    
    # Return confirmation message with tracking ID
    return f"Your appointment has been confirmed. Your tracking ID is {appointment_id}. Please keep this number for your records."

async def store_miscellaneous_requests_in_db(
    requester_name: str,
    requester_phone: str,
    requester_email: str,
    request_type: RequestType,
    request_summary: str
) -> str:
    """
    Stores miscellaneous business development requests in the database.
    Currently, it only prints the request details to the console.
    
    Args:
        requester_name (str): The name of the requester
        requester_phone (str): The phone number of the requester
        requester_email (str): The email address of the requester
        request_type (RequestType): The type of request (SELLING_SERVICES, EMPLOYMENT_REQUEST, OTHER)
        request_summary (str): A summary of the request
    
    Returns:
        str: Confirmation message
    """
    # Print request details to the console
    print(f"BUSINESS DEVELOPMENT REQUEST")
    print(f"Requester: {requester_name}")
    print(f"Phone: {requester_phone}")
    print(f"Email: {requester_email}")
    print(f"Request Type: {request_type}")
    print(f"Summary: {request_summary}")
    
    # Return confirmation message
    return f"Thank you. Your {request_type.lower().replace('_', ' ')} has been recorded. We will review it and get back to you if needed."

async def store_customer_suggestions_in_db(suggestion_summary: str, appointment_id: Optional[str] = None) -> None:
    """
    This function stores the final summary of customer suggestions in a database.
    It should only be called once when all customer suggestions are finished.
    Currently, it only prints the final summary to the console.
    In the future, this may be connected to a hook for database storage.
    
    Args:
        suggestion_summary (str): The final summary of all customer suggestions
        appointment_id (Optional[str]): The tracking ID of the appointment if the feedback is related to a specific appointment
    
    Returns:
        None
    """
    # Print the final summary of customer suggestions to the console
    if suggestion_summary:
        if appointment_id:
            print(f"Customer Suggestions Summary for Appointment #{appointment_id}: {suggestion_summary}")
        else:
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

class AppointmentAgent(Agent):
    """
    Specialized agent for managing appointments (setting new appointments,
    following up pending appointments, etc.)
    """
    def __init__(self) -> None:
        instructions = """You are Naya, a specialized appointment agent for a plumbing company.

CORE PRINCIPLES:
- Be concise and clear in your responses, optimizing for voice communication
- Speak naturally with appropriate pauses and conversational rhythm
- Prioritize user needs and respond directly to their queries
- Maintain a consistent, friendly, and reassuring tone throughout conversations
- Provide professional yet approachable support, ensuring customers feel heard and cared for

CAPABILITIES:
- Schedule new appointments for plumbing services
- Reschedule or cancel existing appointments
- Follow up on pending appointments
- Check available technician time slots
- Gather all necessary details for appointments (name, address, contact info, zip code, issue description)
- While collecting address number, verify that the address is a valid US address. If the address belongs to another country, inform the user that services are only available in the United States
- While collecting zip code number, verify that the zip code is a valid US zip code.
- While collecting contact number, ask the customer to provide their number starting with the area code. the final received number must contain 10 digits.
- Confirm appointment details with customers

INTERACTION GUIDELINES:
- Begin by acknowledging that you're the appointment specialist
- Gather all necessary information systematically
- Confirm understanding before finalizing any appointment
- Provide clear confirmation of appointment details
- Thank the customer for choosing our plumbing services

RESPONSE STYLE:
- Keep responses brief and to the point (typically 1–3 sentences)
- Use simple, clear language without technical jargon
- Be friendly and professional
- When reading text aloud, ignore all markup symbols. Do not verbalize characters such as asterisks, underscores, or brackets. Speak only the plain content
"""
        tools = [
            function_tool(
                get_technician_available_times_from_db,
                name="get_technician_available_times",
                description="Get available time slots for technician appointments. If a technician name is provided, only returns times for that technician."
            ),
            function_tool(
                book_appointment_in_db,
                name="book_appointment_in_db",
                description="Book an appointment in the database and generate a tracking ID. Call this when the customer has selected a timeslot and is ready to book."
            ),
            function_tool(
                find_active_appointments_for_customer,
                name="find_active_appointments_for_customer",
                description="Find all active appointments for a given customer. Use this when a customer wants to check their existing appointments."
            ),
            function_tool(
                cancel_appointments_by_tracking_ids,
                name="cancel_appointments_by_tracking_ids",
                description="Cancel appointments with the given tracking IDs. To modify an appointment, cancel the existing one and book a new one with the updated information."
            )
        ]
        super().__init__(
            instructions=instructions,
            tools=tools,
            tts=CleanTTS(model="sonic-2", voice=voices["appointment_specialist"])
        )
    
    async def on_enter(self) -> None:
        """Called when this agent becomes active"""
        # Get user data to check for problem description
        userdata = self.session.userdata
        
        if userdata.problem_description:
            # Use the problem description in the greeting
            await self.session.generate_reply(
                instructions=f"Greet the user and introduce yourself as the appointment specialist. Mention that you're here to help with their {userdata.problem_description}."
            )
        else:
            # Default greeting if no problem description is available
            await self.session.generate_reply(
                instructions="Greet the user and introduce yourself as the appointment specialist. Ask how you can help with their appointment needs."
            )


class SuggestionAgent(Agent):
    """
    Specialized agent for listening to users suggestions/complaints and storing them
    to be reviewed by managers
    """
    def __init__(self) -> None:
        instructions = """You are Helen, a specialized customer feedback agent for a plumbing company.

CORE PRINCIPLES:
- Be empathetic and understanding when listening to customer feedback
- Take customer suggestions and complaints seriously
- Speak naturally with appropriate pauses and conversational rhythm
- Maintain a consistent, friendly, and reassuring tone throughout conversations
- Make customers feel heard and valued

CAPABILITIES:
- Listen to and document customer suggestions
- Handle customer complaints with empathy
- Collect detailed feedback about our services
- Check if feedback is related to a specific past appointment
- Store feedback for manager review
- Thank customers for their valuable input

INTERACTION GUIDELINES:
- Begin by acknowledging that you're the feedback specialist
- Ask if their feedback is related to a specific appointment they've had in the past
- If yes, use the get_finished_appointments_for_customer function to find their past appointments
- Ask them to identify which appointment their feedback is about
- Include the appointment tracking ID when storing the feedback
- Listen carefully to customer feedback without interrupting
- Ask clarifying questions to ensure you understand their feedback completely
- Summarize their feedback to confirm understanding
- Thank them for taking the time to provide feedback
- Assure them that their feedback will be reviewed by management

RESPONSE STYLE:
- Be empathetic and understanding
- Use active listening techniques
- Acknowledge the customer's feelings
- Be professional but warm
- When reading text aloud, ignore all markup symbols. Do not verbalize characters such as asterisks, underscores, or brackets. Speak only the plain content
"""
        tools = [
            function_tool(
                store_customer_suggestions_in_db,
                name="store_customer_suggestions",
                description="Store customer suggestions in the database. This function should only be called when the customer suggestions are finished. Include the appointment ID if the feedback is related to a specific appointment. It should be called once and only with the summary of customer suggestions."
            ),
            function_tool(
                get_finished_appointments_for_customer,
                name="get_finished_appointments_for_customer",
                description="Find all past/completed appointments for a given customer. Use this when a customer wants to provide feedback about a specific past appointment."
            )
        ]
        super().__init__(
            instructions=instructions,
            tools=tools,
            tts=CleanTTS(model="sonic-2", voice=voices["suggestions_receptionist"])
        )
    
    async def on_enter(self) -> None:
        """Called when this agent becomes active"""
        # Get user data to check for problem description
        userdata = self.session.userdata
        
        if userdata.problem_description:
            # Use the problem description in the greeting
            await self.session.generate_reply(
                instructions=f"Greet the user and introduce yourself as the feedback specialist. Mention that you're here to listen to their feedback about {userdata.problem_description}."
            )
        else:
            # Default greeting if no problem description is available
            await self.session.generate_reply(
                instructions="Greet the user and introduce yourself as the feedback specialist. Express that you're here to listen to their suggestions or concerns."
            )


class BusinessDevelopmentAgent(Agent):
    """
    Specialized agent for handling business development requests, including
    service offerings, employment requests, and partnership opportunities
    """
    def __init__(self) -> None:
        instructions = """You are Marcus, a specialized business development agent for a plumbing company.

CORE PRINCIPLES:
- Be professional and courteous when handling business inquiries
- Evaluate the relevance of requests before storing them
- Collect complete and accurate information from callers with relevant requests
- Speak naturally with appropriate pauses and conversational rhythm
- Maintain a consistent, professional tone throughout conversations
- Be thorough in collecting all necessary details
- Protect the company from irrelevant or potentially malicious requests

CAPABILITIES:
- Handle inquiries from companies wanting to sell services to us
- Process employment requests from job seekers
- Manage partnership or deal proposals from other companies
- Collect contact information and request details
- Evaluate request relevance and filter out inappropriate requests

RELEVANCE CRITERIA:
- Service offerings must be related to plumbing, construction, maintenance, or business operations such as helping us with marketing tools, hiring new staff, a new software which can help our company management or sales, etc.
- Employment requests must be for positions that a plumbing company would reasonably have
- All requests must be professional, legitimate, and non-malicious
- Requests must be specific and detailed enough to evaluate

INTERACTION GUIDELINES:
- Begin by acknowledging that you're the business development specialist
- Determine the type of request (selling services, employment request, or other)
- FIRST EVALUATE if the request is relevant to a plumbing company using the relevance criteria
- If the request is NOT relevant:
  * Politely explain that their request doesn't align with the company's needs
  * Thank them for their interest but decline to proceed further
  * DO NOT collect or store their information
- If the request IS relevant:
  * Collect the requester's name, phone number, and email address
  * Verify that the phone number is in a valid format
  * Verify that the email address is in a valid format
  * For service offerings: collect details about the service, pricing, and company
  * For employment requests: collect educational background, age, work experience, and skills
  * For partnership proposals: collect details about the proposed partnership
  * Summarize the information collected to confirm accuracy
  * Thank them for their interest and explain that their request will be reviewed
  * Store their information using the store_miscellaneous_requests_in_db function

RESPONSE STYLE:
- Be professional and business-like
- Use clear, concise language
- Maintain a helpful and engaged tone
- Be thorough in information collection
- Be firm but polite when declining irrelevant requests
- When reading text aloud, ignore all markup symbols. Do not verbalize characters such as asterisks, underscores, or brackets. Speak only the plain content
"""
        tools = [
            function_tool(
                store_miscellaneous_requests_in_db,
                name="store_miscellaneous_requests_in_db",
                description="Store business development requests in the database. Use this to record service offerings, employment requests, or partnership proposals after collecting all necessary information."
            )
        ]
        super().__init__(
            instructions=instructions,
            tools=tools,
            tts=CleanTTS(model="sonic-2", voice=voices["business_development"])
        )
    
    async def on_enter(self) -> None:
        """Called when this agent becomes active"""
        # Get user data to check for problem description
        userdata = self.session.userdata
        
        if userdata.problem_description:
            # Use the problem description in the greeting
            await self.session.generate_reply(
                instructions=f"Greet the user and introduce yourself as the business development specialist. Mention that you're here to help with their {userdata.problem_description}."
            )
        else:
            # Default greeting if no problem description is available
            await self.session.generate_reply(
                instructions="Greet the user and introduce yourself as the business development specialist. Ask how you can assist them with their business inquiry."
            )

# Standalone handoff functions
async def transfer_to_appointment_agent(context: RunContext, problem_description: Optional[str] = None) -> Agent:
    """
    Transfer the customer to the appointment agent (Naya)
    
    Args:
        context (RunContext): The run context
        problem_description (Optional[str]): Description of the customer's problem
    
    Returns:
        Agent: The appointment agent
    """
    # Get user data from context
    userdata = context.userdata
    
    # Store problem description for context passing
    if problem_description:
        userdata.problem_description = problem_description
    
    # Create appointment agent if it doesn't exist
    if "naya" not in userdata.agents:
        userdata.agents["naya"] = AppointmentAgent()
    
    # Store current agent as previous agent
    userdata.prev_agent = context.session.current_agent
    
    return userdata.agents["naya"]

async def transfer_to_suggestion_agent(context: RunContext, problem_description: Optional[str] = None) -> Agent:
    """
    Transfer the customer to the suggestion agent (Helen)
    
    Args:
        context (RunContext): The run context
        problem_description (Optional[str]): Description of the customer's problem or feedback topic
    
    Returns:
        Agent: The suggestion agent
    """
    # Get user data from context
    userdata = context.userdata
    
    # Store problem description for context passing
    if problem_description:
        userdata.problem_description = problem_description
    
    # Print debug information
    print("Transferring to suggestion agent (Helen)")
    print(f"Current agents in userdata: {list(userdata.agents.keys())}")
    print(f"Problem description: {userdata.problem_description}")
    
    # Create suggestion agent if it doesn't exist
    if "helen" not in userdata.agents:
        print("Creating new SuggestionAgent for Helen")
        userdata.agents["helen"] = SuggestionAgent()
    
    # Store current agent as previous agent
    userdata.prev_agent = context.session.current_agent
    
    # Print confirmation
    print(f"Returning agent: {userdata.agents['helen']}")
    
    return userdata.agents["helen"]

async def transfer_to_business_development_agent(context: RunContext, problem_description: Optional[str] = None) -> Agent:
    """
    Transfer the customer to the business development agent (Marcus)
    
    Args:
        context (RunContext): The run context
        problem_description (Optional[str]): Description of the business inquiry
    
    Returns:
        Agent: The business development agent
    """
    # Get user data from context
    userdata = context.userdata
    
    # Store problem description for context passing
    if problem_description:
        userdata.problem_description = problem_description
    
    # Print debug information
    print("Transferring to business development agent (Marcus)")
    print(f"Current agents in userdata: {list(userdata.agents.keys())}")
    print(f"Problem description: {userdata.problem_description}")
    
    # Create business development agent if it doesn't exist
    if "marcus" not in userdata.agents:
        print("Creating new BusinessDevelopmentAgent for Marcus")
        userdata.agents["marcus"] = BusinessDevelopmentAgent()
    
    # Store current agent as previous agent
    userdata.prev_agent = context.session.current_agent
    
    # Print confirmation
    print(f"Returning agent: {userdata.agents['marcus']}")
    
    return userdata.agents["marcus"]


class Assistant(Agent):
    """
    Base assistant that serves as the initial receptionist and can hand off to
    specialized agents based on customer needs
    """
    def __init__(self) -> None:
        instructions = """You are Anna, a helpful and friendly receptionist for a plumbing company.

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
- Answer general questions about the company's plumbing services
- Determine if the customer needs to speak with a specialized agent
- Hand off to the appointment agent for scheduling service appointments
- Hand off to the suggestion agent for handling customer feedback
- Hand off to the business development agent for business inquiries
- Provide reassurance and simple troubleshooting suggestions when appropriate
- Offer to escalate urgent issues as emergencies
- Engage in casual, friendly conversation to make customers feel comfortable

HANDOFF GUIDELINES:
- If the customer wants to schedule, reschedule, or discuss an appointment, hand off to the appointment agent
- If the customer wants to provide feedback, suggestions, or complaints, hand off to the suggestion agent
- If the customer is from another company wanting to sell services, seeking employment, or proposing a partnership, hand off to the business development agent
- Before handing off, let the customer know you're connecting them with a specialist

LIMITATIONS:
- Acknowledge when you don't know something or when a request is beyond your capabilities
- Do not provide technical repair instructions that require professional service on-site
- Suggest alternatives when you cannot fulfill a request
- Do not make up information or provide misleading answers

RESPONSE STYLE:
- Keep responses brief and to the point (typically 1–3 sentences)
- Use simple, clear language without technical jargon unless requested
- Use a conversational, friendly, and professional tone
- When reading text aloud, ignore all markup symbols. Do not verbalize characters such as asterisks, underscores, or brackets. Speak only the plain content
"""
        tools = [
            function_tool(
                transfer_to_appointment_agent,
                name="transfer_to_appointment_agent",
                description="Transfer the customer to the appointment agent for scheduling, rescheduling, or discussing appointments. Include a description of the customer's problem to provide context."
            ),
            function_tool(
                transfer_to_suggestion_agent,
                name="transfer_to_suggestion_agent",
                description="Transfer the customer to the suggestion agent for handling feedback, suggestions, or complaints. Include a description of the feedback topic to provide context."
            ),
            function_tool(
                transfer_to_business_development_agent,
                name="transfer_to_business_development_agent",
                description="Transfer the customer to the business development agent for handling business inquiries, including service offerings, employment requests, or partnership proposals. Include a description of the business inquiry to provide context."
            )
        ]
        super().__init__(
            instructions=instructions,
            tools=tools,
            tts=CleanTTS(model="sonic-2", voice=voices["receptionist"])
        )
    
    async def on_enter(self) -> None:
        """Called when this agent becomes active"""
        await self.session.generate_reply(
            instructions="Greet the user and offer your assistance as the receptionist."
        )


async def entrypoint(ctx: agents.JobContext):
    # Create user data for the session
    userdata = UserData()
    
    # Create the main assistant (Anna)
    userdata.agents["anna"] = Assistant()
    
    # Pre-initialize other agents to ensure they're available
    userdata.agents["naya"] = AppointmentAgent()
    userdata.agents["helen"] = SuggestionAgent()
    userdata.agents["marcus"] = BusinessDevelopmentAgent()
    
    # Print debug information
    print(f"Initialized agents: {list(userdata.agents.keys())}")
    
    # Create session with a single voice for all agents
    session = AgentSession(
        userdata=userdata,
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=openai.LLM(model="gpt-4o-mini"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=userdata.agents["anna"],
        room_input_options=RoomInputOptions(
            # Using BVCTelephony for better noise cancellation on input
            noise_cancellation=noise_cancellation.BVCTelephony(),
        ),
    )
    
    # No need to call generate_reply here as it's handled by the on_enter method in each agent


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
