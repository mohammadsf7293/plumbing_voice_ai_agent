"""LiveKit tools backed by the current call's demo store."""
from enum import Enum
from livekit.agents import RunContext, ToolError


class RequestType(str, Enum):
    SELLING_SERVICES = "SELLING_SERVICES"
    EMPLOYMENT_REQUEST = "EMPLOYMENT_REQUEST"
    OTHER = "OTHER"


async def get_technician_available_times_from_db(context: RunContext, technician_name: str | None = None) -> list[str]:
    """List the current call's available demo slots, optionally by technician."""
    return context.userdata.store.available(technician_name)


async def book_appointment_in_db(context: RunContext, customer_name: str, agent_name: str,
                                 timeslot: str, address: str, phone: str, zip_code: str) -> str:
    """Book a demo slot. agent_name is the technician's name from availability.

    address must use '123 Main St, Austin, TX'; phone must be a US number.
    """
    try:
        booking = context.userdata.store.book(customer_name, agent_name, timeslot, address, phone, zip_code)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    return f"Your demo appointment has been confirmed. Your tracking ID is {booking.tracking_id}. This is a simulation; no technician will be dispatched."


async def cancel_appointments_by_tracking_ids(context: RunContext, tracking_ids: list[int]) -> str:
    """Cancel existing appointments in this demo call."""
    try:
        context.userdata.store.cancel(tracking_ids)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    return "Demo appointments cancelled: " + ", ".join(map(str, tracking_ids))


async def find_active_appointments_for_customer(context: RunContext, customer_name: str) -> list[str]:
    """Find appointments actually booked during this call."""
    return context.userdata.store.history(customer_name, "active")


async def get_finished_appointments_for_customer(context: RunContext, customer_name: str) -> list[str]:
    """Find completed demo appointments; an unseeded session returns no results."""
    return context.userdata.store.history(customer_name, "completed")


async def store_customer_suggestions_in_db(context: RunContext, suggestion_summary: str,
                                          appointment_id: str | None = None) -> str:
    """Keep feedback in memory for this call only."""
    if not suggestion_summary.strip():
        raise ToolError("Please provide a feedback summary before submitting.")
    if appointment_id is not None:
        if not appointment_id.isascii() or not appointment_id.isdigit() or int(appointment_id) not in context.userdata.store.bookings:
            raise ToolError("That appointment was not found in this demo session.")
    context.userdata.store.feedback.append({"summary": suggestion_summary.strip(), "appointment_id": appointment_id})
    return "Feedback saved for this demo session only."


async def store_miscellaneous_requests_in_db(context: RunContext, requester_name: str,
                                            requester_phone: str, requester_email: str,
                                            request_type: RequestType, request_summary: str) -> str:
    """Keep a business inquiry in memory for this call only."""
    if not all(value.strip() for value in (requester_name, requester_phone, requester_email, request_summary)):
        raise ToolError("Please collect a name, phone, email, and summary before submitting.")
    context.userdata.store.inquiries.append({"name": requester_name.strip(), "phone": requester_phone,
        "email": requester_email, "type": request_type, "summary": request_summary.strip()})
    return "Inquiry saved for this demo session only."
