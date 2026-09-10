from datetime import date, datetime
from types import SimpleNamespace
import asyncio
import pytest
from livekit.agents import ToolError
from plumbing.business import DemoStore, validate_customer
from plumbing.state import UserData
from plumbing.tools import (book_appointment_in_db, cancel_appointments_by_tracking_ids,
    find_active_appointments_for_customer, get_finished_appointments_for_customer,
    store_customer_suggestions_in_db, store_miscellaneous_requests_in_db, RequestType)


@pytest.fixture
def store():
    return DemoStore(today=date(2026, 12, 30))


def details(store, **overrides):
    technician, timeslot = store.slots()[0]
    return dict(customer_name="Alex Example", technician=technician, timeslot=timeslot,
                address="123 Main St, Austin, TX", phone="(512) 555-0123", zip_code="78701") | overrides


def test_availability_is_repeatable_and_rolls_over_year(store):
    assert store.available() == DemoStore(today=store.today).available()
    assert len(store.available("John Smith")) == 3
    assert store.available("Unknown") == []
    dates = [datetime.strptime(slot.split()[0], "%Y/%m/%d").date() for _, slot in store.slots()]
    assert min(dates) > store.today
    assert date(2027, 1, 2) in dates


@pytest.mark.parametrize('overrides', [
    {'customer_name': ' '}, {'address': 'Paris, France'}, {'address': '123 Main St, Austin, ZZ'},
    {'phone': '123'}, {'phone': '512ABC5550123'}, {'phone': '1125550123'},
    {'zip_code': '1234'}, {'zip_code': 'ABCDE'}, {'zip_code': '１２３４５'},
    {'technician': 'Unknown'}, {'timeslot': '2025/09/08 9:00 AM - 10:00 AM'},
])
def test_invalid_booking_has_no_side_effects(store, overrides):
    with pytest.raises(ValueError):
        store.book(**details(store, **overrides))
    assert store.bookings == {}
    assert store.next_id == 100001


def test_phone_normalization():
    assert validate_customer('Alex', '123 Main St, Austin, TX', '+1 (512) 555-0123', '78701-1234') == '5125550123'


def test_booking_retry_conflict_cancellation_and_history(store):
    booking = store.book(**details(store))
    assert store.book(**details(store)) is booking
    assert len(store.bookings) == 1
    assert len(store.available()) == 8
    assert str(booking.tracking_id) in store.history(' alex example ', 'active')[0]
    with pytest.raises(ValueError, match='no longer available'):
        store.book(**details(store, customer_name='Someone Else'))
    with pytest.raises(ValueError):
        store.cancel([booking.tracking_id, 999999])
    assert booking.status == 'active'  # Batch cancellation is all-or-nothing.
    store.cancel([booking.tracking_id])
    store.cancel([booking.tracking_id])  # Retrying cancellation is safe.
    assert store.history('Alex Example', 'active') == []
    assert len(store.available()) == 9
    assert store.book(**details(store)).tracking_id != booking.tracking_id


async def test_tool_workflow_and_session_isolation(store):
    context = SimpleNamespace(userdata=UserData(store=store))
    args = details(store)
    args['agent_name'] = args.pop('technician')
    # Concurrent retries run against the actual tool boundary.
    results = await asyncio.gather(*(book_appointment_in_db(context, **args) for _ in range(3)))
    assert len(set(results)) == 1
    assert len(store.bookings) == 1
    assert await find_active_appointments_for_customer(context, 'Alex Example')
    assert await get_finished_appointments_for_customer(context, 'Alex Example') == []
    assert UserData().store.bookings == {}
    with pytest.raises(ToolError):
        await book_appointment_in_db(context, **(args | {'phone': 'bad'}))
    await store_customer_suggestions_in_db(context, 'Helpful technician', '100001')
    assert store.feedback[0]['appointment_id'] == '100001'
    with pytest.raises(ToolError):
        await store_customer_suggestions_in_db(context, 'Feedback', '999999')
    with pytest.raises(ToolError):
        await store_customer_suggestions_in_db(context, ' ')
    await store_miscellaneous_requests_in_db(context, 'Alex', '5125550123', 'alex@example.com', RequestType.OTHER, 'Partnership')
    assert len(store.inquiries) == 1
    with pytest.raises(ToolError):
        await store_miscellaneous_requests_in_db(context, '', '', '', RequestType.OTHER, '')
    with pytest.raises(ToolError):
        await cancel_appointments_by_tracking_ids(context, [])
    await cancel_appointments_by_tracking_ids(context, [100001])
    assert not await find_active_appointments_for_customer(context, 'Alex Example')
