import sqlite3
from datetime import date, timedelta

from app.scheduler import (
    DATABASE_FILE,
    create_appointment,
    get_appointments,
)


def get_test_weekday():
    test_date = date.today() + timedelta(days=7)

    while test_date.weekday() >= 5:
        test_date += timedelta(days=1)

    return test_date.strftime("%Y-%m-%d")


def test_successful_booking_creates_appointment():
    test_date = get_test_weekday()

    result = create_appointment(
        name="Task Three Test",
        email="task3@example.com",
        phone="9999999999",
        date=test_date,
        start_time="11:00",
        duration=30,
        purpose="Task 3 booking test",
    )

    assert result["success"] is True
    assert result["appointment_id"] is not None
    assert result["date"] == test_date
    assert result["start_time"] == "11:00"
    assert result["end_time"] == "11:30"


def test_double_booking_is_rejected():
    test_date = get_test_weekday()

    first = create_appointment(
        name="First Booking",
        email="first@example.com",
        phone="9999999991",
        date=test_date,
        start_time="13:00",
        duration=30,
        purpose="First booking",
    )

    assert first["success"] is True

    second = create_appointment(
        name="Second Booking",
        email="second@example.com",
        phone="9999999992",
        date=test_date,
        start_time="13:00",
        duration=30,
        purpose="Second booking",
    )

    assert second["success"] is False
    assert "available_slots" in second


def test_overlapping_booking_is_rejected():
    test_date = get_test_weekday()

    first = create_appointment(
        name="Overlap First",
        email="overlap1@example.com",
        phone="9999999993",
        date=test_date,
        start_time="14:00",
        duration=60,
        purpose="Overlap test",
    )

    assert first["success"] is True

    second = create_appointment(
        name="Overlap Second",
        email="overlap2@example.com",
        phone="9999999994",
        date=test_date,
        start_time="14:30",
        duration=30,
        purpose="Overlap test",
    )

    assert second["success"] is False


def test_adjacent_booking_is_allowed():
    test_date = get_test_weekday()

    first = create_appointment(
        name="Adjacent First",
        email="adjacent1@example.com",
        phone="9999999995",
        date=test_date,
        start_time="15:00",
        duration=30,
        purpose="Adjacent test",
    )

    assert first["success"] is True

    second = create_appointment(
        name="Adjacent Second",
        email="adjacent2@example.com",
        phone="9999999996",
        date=test_date,
        start_time="15:30",
        duration=30,
        purpose="Adjacent test",
    )

    assert second["success"] is True


def test_booking_outside_business_hours_is_rejected():
    test_date = get_test_weekday()

    result = create_appointment(
        name="Outside Hours",
        email="outside@example.com",
        phone="9999999997",
        date=test_date,
        start_time="17:30",
        duration=60,
        purpose="Outside hours test",
    )

    assert result["success"] is False


def test_booking_on_weekend_is_rejected():
    test_date = date.today()

    while test_date.weekday() < 5:
        test_date += timedelta(days=1)

    result = create_appointment(
        name="Weekend Test",
        email="weekend@example.com",
        phone="9999999998",
        date=test_date.strftime("%Y-%m-%d"),
        start_time="10:00",
        duration=30,
        purpose="Weekend test",
    )

    assert result["success"] is False