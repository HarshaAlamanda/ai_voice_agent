from datetime import date, timedelta

from app.scheduler import (
    is_within_business_hours,
    check_availability,
    find_available_slots,
)


def test_valid_weekday_and_business_hours():
    # Monday
    valid, message = is_within_business_hours(
        "2026-10-12",
        "09:00",
        30,
    )

    assert valid is True


def test_meeting_before_business_hours_is_rejected():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "08:30",
        30,
    )

    assert valid is False


def test_meeting_after_business_hours_is_rejected():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "18:30",
        30,
    )

    assert valid is False


def test_weekend_is_rejected():
    # Saturday
    valid, message = is_within_business_hours(
        "2026-10-17",
        "10:00",
        30,
    )

    assert valid is False


def test_zero_duration_is_rejected():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "10:00",
        0,
    )

    assert valid is False


def test_negative_duration_is_rejected():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "10:00",
        -30,
    )

    assert valid is False


def test_standard_30_minute_slot_is_valid():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "10:00",
        30,
    )

    assert valid is True


def test_meeting_ending_at_business_close_is_valid():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "17:30",
        30,
    )

    assert valid is True


def test_meeting_extending_past_business_close_is_rejected():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "18:00",
        30,
    )

    assert valid is False


def test_60_minute_meeting_ending_at_business_close_is_valid():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "17:00",
        60,
    )

    assert valid is True


def test_60_minute_meeting_extending_past_business_close_is_rejected():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "17:30",
        60,
    )

    assert valid is False


def test_120_minute_meeting_within_business_hours_is_valid():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "16:00",
        120,
    )

    assert valid is True


def test_120_minute_meeting_extending_past_business_hours_is_rejected():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "16:30",
        120,
    )

    assert valid is False


def test_invalid_date_is_rejected():
    valid, message = is_within_business_hours(
        "2026-99-99",
        "10:00",
        30,
    )

    assert valid is False


def test_invalid_time_is_rejected():
    valid, message = is_within_business_hours(
        "2026-10-12",
        "25:00",
        30,
    )

    assert valid is False


def test_available_slot_returns_true():
    test_date = (
        date.today() + timedelta(days=7)
    )

    # Move forward until a weekday.
    while test_date.weekday() >= 5:
        test_date += timedelta(days=1)

    date_string = test_date.strftime("%Y-%m-%d")

    assert check_availability(
        date_string,
        "10:00",
        30,
    ) is True


def test_find_available_slots_returns_slots():
    test_date = (
        date.today() + timedelta(days=7)
    )

    while test_date.weekday() >= 5:
        test_date += timedelta(days=1)

    date_string = test_date.strftime("%Y-%m-%d")

    slots = find_available_slots(
        date_string,
        30,
    )

    assert isinstance(slots, list)