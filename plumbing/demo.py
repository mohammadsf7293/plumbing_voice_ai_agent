"""Scripted business workflow; no LLM, microphone, or subscription needed."""
from .business import DemoStore


def main() -> None:
    store = DemoStore()
    technician, timeslot = store.slots()[0]
    print("Offline demo — scripted workflow, not an AI conversation")
    print(f"Available: {technician}, {timeslot}")
    details = dict(customer_name="Alex Example", technician=technician, timeslot=timeslot,
                   address="123 Main St, Austin, TX", phone="512-555-0123", zip_code="78701")
    try:
        store.book(**(details | {"phone": "123"}))
    except ValueError as error:
        print(f"Invalid phone rejected: {error}")
    booking = store.book(**details)
    print(f"Booked: {booking.tracking_id}; available slots: {len(store.available())}")
    retry = store.book(**details)
    print(f"Retry returned same booking: {retry.tracking_id == booking.tracking_id}")
    print(f"Active appointments: {len(store.history('Alex Example', 'active'))}")
    store.cancel([booking.tracking_id])
    print(f"Cancelled: {booking.tracking_id}; available slots: {len(store.available())}")


if __name__ == '__main__':
    main()
