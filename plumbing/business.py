"""Deterministic, session-local demo storage. No external services required."""

from dataclasses import dataclass, field
from datetime import date, timedelta
import re

STATES = frozenset("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC".split())
TECHNICIANS = ("John Smith", "Maria Garcia", "David Johnson")


def validate_customer(name: str, address: str, phone: str, zip_code: str) -> str:
    """Check US input format; this does not verify address deliverability."""
    if not name.strip():
        raise ValueError("Please provide the customer's name.")
    if not re.fullmatch(r"[0-9]{5}(?:-[0-9]{4})?", zip_code):
        raise ValueError("Please provide a five-digit US ZIP code or ZIP+4.")
    # Require street number, street, city, and a supported state abbreviation.
    parts = [part.strip() for part in address.split(",")]
    if (len(parts) != 3 or not re.fullmatch(r"[0-9]+\s+\S.*", parts[0])
            or not parts[1] or parts[2].upper() not in STATES):
        raise ValueError("Please use a US address in the format 123 Main St, Austin, TX.")
    if not re.fullmatch(r"[0-9 ()+.-]+", phone):
        raise ValueError("Please provide a ten-digit US phone number.")
    digits = re.sub(r"[^0-9]", "", phone)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if not re.fullmatch(r"[2-9][0-9]{2}[2-9][0-9]{6}", digits):
        raise ValueError("Please provide a ten-digit US phone number with a valid area code and exchange.")
    return digits


@dataclass
class Booking:
    tracking_id: int
    customer_name: str
    technician: str
    timeslot: str
    address: str
    phone: str
    zip_code: str
    status: str = "active"


@dataclass
class DemoStore:
    """One store per call; fixed clock can be injected for repeatable tests.

    Operations are synchronous with no await points, so a booking's validation
    and reservation are atomic within the worker's event loop. This is not a
    shared calendar or durable database.
    """

    today: date = field(default_factory=date.today)
    bookings: dict[int, Booking] = field(default_factory=dict)
    feedback: list[dict] = field(default_factory=list)
    inquiries: list[dict] = field(default_factory=list)
    next_id: int = 100001

    def slots(self) -> list[tuple[str, str]]:
        return [(name, f"{self.today + timedelta(days=offset):%Y/%m/%d} 9:00 AM - 10:00 AM")
                for offset in range(1, 4) for name in TECHNICIANS]

    def available(self, technician: str | None = None) -> list[str]:
        reserved = {(b.technician, b.timeslot) for b in self.bookings.values() if b.status == "active"}
        return [f"{name},{slot}" for name, slot in self.slots()
                if (technician is None or technician == name) and (name, slot) not in reserved]

    def book(self, customer_name: str, technician: str, timeslot: str,
             address: str, phone: str, zip_code: str) -> Booking:
        phone = validate_customer(customer_name, address, phone, zip_code)
        customer_name = customer_name.strip()
        address = address.strip()
        if (technician, timeslot) not in self.slots():
            raise ValueError("Please select a technician and timeslot from the available appointments.")
        for booking in self.bookings.values():
            if booking.status == "active" and (booking.technician, booking.timeslot) == (technician, timeslot):
                if (booking.customer_name.casefold(), booking.phone, booking.address.casefold(), booking.zip_code) == (customer_name.casefold(), phone, address.casefold(), zip_code):
                    return booking  # A repeated tool call must not create another booking.
                raise ValueError("That timeslot is no longer available. Please choose another.")
        booking = Booking(self.next_id, customer_name, technician, timeslot, address, phone, zip_code)
        self.bookings[booking.tracking_id] = booking
        self.next_id += 1
        return booking

    def cancel(self, tracking_ids: list[int]) -> None:
        if not tracking_ids:
            raise ValueError("Please provide at least one tracking ID.")
        if any(type(value) is not int or value not in self.bookings for value in tracking_ids):
            raise ValueError("An appointment was not found. Please check the tracking IDs.")
        for tracking_id in tracking_ids:
            self.bookings[tracking_id].status = "cancelled"

    def history(self, customer_name: str, status: str) -> list[str]:
        return [f"{b.tracking_id},{b.technician},{b.timeslot}" for b in self.bookings.values()
                if b.customer_name.casefold() == customer_name.strip().casefold() and b.status == status]
