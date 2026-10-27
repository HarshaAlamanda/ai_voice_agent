from datetime import date, timedelta

from app.agent import confirm_booking
from app.conversation import ConversationManager
from app.scheduler import get_appointments


def get_test_weekday():
    test_date = date.today() + timedelta(days=14)

    while test_date.weekday() >= 5:
        test_date += timedelta(days=1)

    return test_date.strftime("%Y-%m-%d")


def test_confirm_booking_creates_appointment():
    manager = ConversationManager()

    test_date = get_test_weekday()

    manager.update(
        caller_name="Confirmation Test",
        caller_email="confirmation@example.com",
        caller_phone="9999999999",
        meeting_requested=True,
        meeting_date=test_date,
        meeting_time="10:00",
        meeting_duration=30,
        meeting_purpose="Confirmation flow test",
        awaiting_confirmation=True,
    )

    response = confirm_booking(manager)

    state = manager.get_state()

    assert state.confirmed is True
    assert state.awaiting_confirmation is False
    assert "booked" in response.lower()


def test_confirm_booking_rejects_already_booked_slot():
    manager = ConversationManager()

    test_date = get_test_weekday()

    manager.update(
        caller_name="Second Confirmation Test",
        caller_email="secondconfirmation@example.com",
        caller_phone="9999999998",
        meeting_requested=True,
        meeting_date=test_date,
        meeting_time="11:00",
        meeting_duration=30,
        meeting_purpose="Double booking confirmation test",
        awaiting_confirmation=True,
    )

    # First booking takes the slot.
    from app.scheduler import create_appointment

    first = create_appointment(
        name="First Caller",
        email="firstcaller@example.com",
        phone="9999999997",
        date=test_date,
        start_time="11:00",
        duration=30,
        purpose="Takes the slot",
    )

    assert first["success"] is True

    # Second caller confirms the same slot.
    response = confirm_booking(manager)

    state = manager.get_state()

    assert state.confirmed is False
    assert state.awaiting_confirmation is False
    assert (
        "taken" in response.lower()
        or "available" in response.lower()
        or "book" in response.lower()
    )


def test_confirm_booking_requires_required_information():
    manager = ConversationManager()

    manager.update(
        caller_name="Incomplete Test",
        caller_email="incomplete@example.com",
        meeting_date=None,
        meeting_time=None,
        meeting_purpose=None,
        awaiting_confirmation=True,
    )

    response = confirm_booking(manager)

    state = manager.get_state()

    assert state.confirmed is False
    assert state.awaiting_confirmation is False
    assert response


def test_confirm_booking_returns_booking_confirmation():
    manager = ConversationManager()

    test_date = get_test_weekday()

    manager.update(
        caller_name="Booking ID Test",
        caller_email="bookingid@example.com",
        caller_phone="9999999996",
        meeting_requested=True,
        meeting_date=test_date,
        meeting_time="12:00",
        meeting_duration=30,
        meeting_purpose="Booking ID confirmation test",
        awaiting_confirmation=True,
    )

    response = confirm_booking(manager)

    assert "booked" in response.lower()