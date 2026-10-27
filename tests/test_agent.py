from app.conversation import ConversationManager


def test_booking_information_is_stored():
    manager = ConversationManager()

    manager.update(
        caller_name="Harsha",
        caller_email="harsha@example.com",
        meeting_date="2026-10-15",
        meeting_time="15:00",
        meeting_purpose="Project discussion",
    )

    state = manager.get_state()

    assert state.caller_name == "Harsha"
    assert state.caller_email == "harsha@example.com"
    assert state.meeting_date == "2026-10-15"
    assert state.meeting_time == "15:00"
    assert state.meeting_purpose == "Project discussion"


def test_date_correction_replaces_previous_date():
    manager = ConversationManager()

    manager.update(
        caller_name="Harsha",
        meeting_date="2026-10-14",
        meeting_time="15:00",
        meeting_purpose="Project discussion",
    )

    manager.update(
        meeting_date="2026-10-15"
    )

    state = manager.get_state()

    assert state.meeting_date == "2026-10-15"
    assert state.caller_name == "Harsha"
    assert state.meeting_time == "15:00"
    assert state.meeting_purpose == "Project discussion"


def test_time_correction_replaces_previous_time():
    manager = ConversationManager()

    manager.update(
        caller_name="Harsha",
        meeting_date="2026-10-15",
        meeting_time="03:00",
        meeting_purpose="Project discussion",
    )

    manager.update(
        meeting_time="16:00"
    )

    state = manager.get_state()

    assert state.meeting_time == "16:00"
    assert state.meeting_date == "2026-10-15"
    assert state.caller_name == "Harsha"
    assert state.meeting_purpose == "Project discussion"


def test_date_change_preserves_everything_else():
    manager = ConversationManager()

    manager.update(
        caller_name="Harsha",
        caller_email="harsha@example.com",
        meeting_date="2026-10-14",
        meeting_time="16:00",
        meeting_purpose="AI project discussion",
    )

    manager.update(
        meeting_date="2026-10-09"
    )

    state = manager.get_state()

    assert state.meeting_date == "2026-10-09"
    assert state.caller_name == "Harsha"
    assert state.caller_email == "harsha@example.com"
    assert state.meeting_time == "16:00"
    assert state.meeting_purpose == "AI project discussion"


def test_ready_for_confirmation_requires_required_information():
    manager = ConversationManager()

    manager.update(
        caller_name="Harsha",
        meeting_date="2026-10-15",
        meeting_time="16:00",
        meeting_purpose="AI project discussion",
    )

    assert manager.is_ready_for_confirmation() is True


def test_missing_information_is_reported():
    manager = ConversationManager()

    manager.update(
        caller_name="Harsha",
        meeting_date="2026-10-15",
    )

    missing = manager.get_missing_booking_information()

    assert "email" in missing
    assert "time" in missing
    assert "purpose" in missing

    assert "name" not in missing
    assert "date" not in missing


def test_reset_clears_conversation_state():
    manager = ConversationManager()

    manager.update(
        caller_name="Harsha",
        caller_email="harsha@example.com",
        meeting_date="2026-10-15",
        meeting_time="16:00",
        meeting_purpose="AI project discussion",
    )

    manager.reset()

    state = manager.get_state()

    assert state.caller_name is None
    assert state.caller_email is None
    assert state.meeting_date is None
    assert state.meeting_time is None
    assert state.meeting_purpose is None
from app.agent import (
    apply_local_information,
    extract_simple_booking_information,
)
from app.date_resolver import resolve_relative_date


def test_agent_correction_actually_thursday():
    manager = ConversationManager()

    manager.update(
        meeting_requested=True,
        caller_name="Harsha",
        caller_email="harsha@example.com",
        meeting_time="15:00",
        meeting_purpose="Project discussion",
    )

    information = extract_simple_booking_information(
        "Actually Thursday.",
        manager,
    )

    apply_local_information(
        information,
        manager,
    )

    expected_date = resolve_relative_date(
        "thursday"
    )

    state = manager.get_state()

    assert state.meeting_date == expected_date
    assert state.meeting_time == "15:00"
    assert state.meeting_purpose == "Project discussion"


def test_agent_correction_no_4_pm():
    manager = ConversationManager()

    manager.update(
        meeting_requested=True,
        caller_name="Harsha",
        caller_email="harsha@example.com",
        meeting_date="2026-10-15",
        meeting_time="15:00",
        meeting_purpose="Project discussion",
    )

    information = extract_simple_booking_information(
        "No, 4 PM.",
        manager,
    )

    apply_local_information(
        information,
        manager,
    )

    state = manager.get_state()

    assert state.meeting_time == "16:00"
    assert state.meeting_date == "2026-10-15"
    assert state.meeting_purpose == "Project discussion"


def test_agent_change_meeting_to_tomorrow():
    manager = ConversationManager()

    manager.update(
        meeting_requested=True,
        caller_name="Harsha",
        caller_email="harsha@example.com",
        meeting_date="2026-10-15",
        meeting_time="16:00",
        meeting_purpose="Project discussion",
    )

    information = extract_simple_booking_information(
        "Change the meeting to tomorrow.",
        manager,
    )

    apply_local_information(
        information,
        manager,
    )

    expected_date = resolve_relative_date(
        "tomorrow"
    )

    state = manager.get_state()

    assert state.meeting_date == expected_date
    assert state.meeting_time == "16:00"
    assert state.meeting_purpose == "Project discussion"


def test_agent_correction_does_not_erase_existing_information():
    manager = ConversationManager()

    manager.update(
        meeting_requested=True,
        caller_name="Harsha",
        caller_email="harsha@example.com",
        meeting_date="2026-10-15",
        meeting_time="15:00",
        meeting_purpose="Discuss AI project",
    )

    information = extract_simple_booking_information(
        "No, 4 PM.",
        manager,
    )

    apply_local_information(
        information,
        manager,
    )

    state = manager.get_state()

    assert state.meeting_time == "16:00"

    # Existing information must survive the correction.
    assert state.caller_name == "Harsha"
    assert state.caller_email == "harsha@example.com"
    assert state.meeting_date == "2026-10-15"
    assert state.meeting_purpose == "Discuss AI project"
from app.agent import ask_agent


def test_cancel_pending_booking_does_not_create_appointment():
    manager = ConversationManager()

    manager.update(
        meeting_requested=True,
        caller_name="Test Caller",
        caller_email="test.caller@example.com",
        meeting_date="2027-02-11",
        meeting_time="15:00",
        meeting_purpose="Cancellation test",
        awaiting_confirmation=True,
    )

    response = ask_agent(
        "Cancel it",
        manager,
    )

    state = manager.get_state()

    assert state.awaiting_confirmation is False
    assert state.confirmed is False
    assert "won't book it" in response.lower()


def test_reset_clears_pending_confirmation():
    manager = ConversationManager()

    manager.update(
        meeting_requested=True,
        caller_name="Test Caller",
        caller_email="test.caller@example.com",
        meeting_date="2027-02-11",
        meeting_time="15:00",
        meeting_purpose="Reset test",
        awaiting_confirmation=True,
    )

    manager.reset()

    state = manager.get_state()

    assert state.caller_name is None
    assert state.caller_email is None
    assert state.meeting_date is None
    assert state.meeting_time is None
    assert state.meeting_purpose is None
    assert state.meeting_requested is False
    assert state.awaiting_confirmation is False
    assert state.confirmed is False