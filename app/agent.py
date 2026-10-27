
from __future__ import annotations

import json
import logging
import re
from datetime import date, datetime
from typing import Optional

from app.contacts import build_contacts_prompt
from app.context import build_context_prompt
from app.conversation import ConversationManager
from app.date_resolver import normalize_time, resolve_relative_date
from app.gemini_client import ask_gemini
from app.scheduler import (
    cancel_appointment,
    check_availability,
    create_appointment,
    find_available_slots,
    find_appointments_by_email,
    is_within_business_hours,
)


BOOKING_PATTERNS = [
    r"\bbook\b",
    r"\bbooking\b",
    r"\bschedule\b",
    r"\bscheduling\b",
    r"\bmeeting\b",
    r"\bappointment\b",
    r"\barrange\b",
    r"\bset\s*up\b",
    r"\btalk\s+to\b",
    r"\bspeak\s+to\b",
    r"\bmeet\s+with\b",
    r"\bwant\s+to\s+meet\b",
    r"\bwould\s+like\s+to\s+meet\b",
    r"\bneed\s+to\s+meet\b",
    r"\bneed\s+a\s+meeting\b",
    r"\bcan\s+i\s+meet\b",
    r"\bcould\s+i\s+meet\b",
    r"\bwant\s+to\s+speak\b",
    r"\bwant\s+to\s+talk\b",
]


DATE_WORDS = {
    "today", "tomorrow", "tmrw", "tommorow",
    "day after tomorrow", "day after tmrw",
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday",
}


def contains_booking_intent(text: str) -> bool:
    return any(
        re.search(pattern, text.lower())
        for pattern in BOOKING_PATTERNS
    )


def extract_email(text: str) -> Optional[str]:
    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
    )
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    matches = re.findall(
        r"(?<!\d)(?:\+?\d[\d\s\-()]{7,}\d)(?!\d)",
        text,
    )

    for phone in matches:
        digits = re.sub(r"\D", "", phone)
        if 8 <= len(digits) <= 15:
            return phone.strip()

    return None


def extract_time_from_text(text: str) -> Optional[str]:
    patterns = [
        r"\b\d{1,2}:\d{2}\s*(?:am|pm)\b",
        r"\b\d{1,2}\s*(?:am|pm)\b",
        r"\b\d{1,2}:\d{2}\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())

        if match:
            normalized = normalize_time(match.group(0))
            if normalized:
                return normalized

    return None


def extract_date_from_text(text: str) -> Optional[str]:
    lowered = text.lower().strip()

    expressions = [
        "day after tomorrow",
        "day after tmrw",
        "next week monday",
        "next week tuesday",
        "next week wednesday",
        "next week thursday",
        "next week friday",
        "next week saturday",
        "next week sunday",
        "monday next week",
        "tuesday next week",
        "wednesday next week",
        "thursday next week",
        "friday next week",
        "saturday next week",
        "sunday next week",
        "coming monday",
        "coming tuesday",
        "coming wednesday",
        "coming thursday",
        "coming friday",
        "coming saturday",
        "coming sunday",
        "next monday",
        "next tuesday",
        "next wednesday",
        "next thursday",
        "next friday",
        "next saturday",
        "next sunday",
        "tomorrow",
        "tmrw",
        "tommorow",
        "today",
    ]

    for expression in expressions:
        if expression in lowered:
            resolved = resolve_relative_date(
                expression,
                reference_date=date.today(),
            )
            if resolved:
                return resolved

    for weekday in DATE_WORDS:
        if weekday in lowered:
            resolved = resolve_relative_date(
                weekday,
                reference_date=date.today(),
            )
            if resolved:
                return resolved

    match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", lowered)

    if match:
        return resolve_relative_date(
            match.group(0),
            reference_date=date.today(),
        )

    match = re.search(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b", lowered)

    if match:
        return resolve_relative_date(
            match.group(0),
            reference_date=date.today(),
        )

    return None


def is_simple_name(text: str) -> bool:
    cleaned = text.strip()

    if not cleaned or len(cleaned) > 50:
        return False

    if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", cleaned):
        return False

    blocked = {
        "yes", "yeah", "yep", "yup", "okay", "ok", "sure",
        "hello", "hi", "hey", "meeting", "appointment",
        "booking", "schedule", "today", "tomorrow",
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday",
    }

    return cleaned.lower() not in blocked


def extract_simple_booking_information(
    text: str,
    manager: ConversationManager,
) -> dict:
    information = {}
    state = manager.get_state()

    if contains_booking_intent(text):
        information["wants_meeting"] = True

    email = extract_email(text)
    if email:
        information["caller_email"] = email

    phone = extract_phone(text)
    if phone:
        information["caller_phone"] = phone

    time_value = extract_time_from_text(text)
    if time_value:
        information["time_text"] = time_value

    date_value = extract_date_from_text(text)
    if date_value:
        information["date_value"] = date_value

    name_match = re.search(
        r"\b(?:my name is|i am|i'm|this is|name's)\s+"
        r"([A-Za-z][A-Za-z .'-]{1,50})",
        text,
        flags=re.IGNORECASE,
    )

    if name_match:
        name = name_match.group(1).strip()

        name = re.split(
            r"\b(?:and|my email|email|phone|number)\b",
            name,
            flags=re.IGNORECASE,
        )[0].strip()

        name = name.rstrip(" .,'-!")

        if name:
            information["caller_name"] = name

    if (
        not information.get("caller_name")
        and not state.caller_name
        and state.meeting_requested
        and is_simple_name(text)
    ):
        information["caller_name"] = text.strip()

    # Improved purpose extraction: works even when the initial request
    # also includes the caller's name, email, date, or time.
    purpose_patterns = (
        r"\b(?:the\s+)?meeting\s+is\s+about\s+(.+?)(?=[.!?]|$)",
        r"\b(?:it\s+is|it's|its)\s+about\s+(.+?)(?=[.!?]|$)",
        r"\b(?:we\s+need\s+to\s+discuss|i\s+(?:want|need)\s+to\s+discuss|"
        r"i'd\s+like\s+to\s+discuss|to\s+discuss|discussing)\s+"
        r"(.+?)(?=[.!?]|$)",
        r"\b(?:the\s+)?purpose\s+is\s+(.+?)(?=[.!?]|$)",
        r"\bregarding\s+(.+?)(?=[.!?]|$)",
    )

    purpose_candidate = ""

    for pattern in purpose_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            purpose_candidate = match.group(1).strip().rstrip(" .,!?")
            break

    # Handle standalone answers when the receptionist is waiting
    # for the meeting purpose.
    if (
        not purpose_candidate
        and state.meeting_requested
        and not state.meeting_purpose
        and not information.get("caller_email")
        and not information.get("caller_phone")
        and not information.get("date_value")
        and not information.get("time_text")
        and not information.get("caller_name")
    ):
        candidate = text.strip()

        standalone_patterns = (
            r"^(?:the\s+)?meeting\s+is\s+about\s+(.+?)\s*[.!?]*$",
            r"^(?:it\s+is|it's|its)\s+about\s+(.+?)\s*[.!?]*$",
            r"^(?:we\s+need\s+to\s+discuss|i\s+(?:want|need)\s+to\s+discuss|"
            r"i'd\s+like\s+to\s+discuss|regarding|to\s+discuss)\s+"
            r"(.+?)\s*[.!?]*$",
            r"^(?:the\s+)?purpose\s+is\s+(.+?)\s*[.!?]*$",
        )

        for pattern in standalone_patterns:
            match = re.match(
                pattern,
                candidate,
                flags=re.IGNORECASE,
            )

            if match:
                purpose_candidate = match.group(1).strip().rstrip(" .,!?")
                break

    blocked_purpose_answers = {
        "yes", "yeah", "yep", "yup", "okay", "ok", "sure",
        "confirm", "confirmed", "go ahead", "no", "nope",
        "cancel", "cancel it", "cancel the booking",
        "cancel the meeting", "stop", "never mind", "nevermind",
    }

    if (
        purpose_candidate
        and purpose_candidate.lower() not in blocked_purpose_answers
        and len(purpose_candidate) <= 200
    ):
        information["meeting_purpose"] = purpose_candidate

    # If all other details are already known, treat a standalone
    # answer as the purpose when that field is still empty.
    if (
        state.meeting_requested
        and state.caller_name
        and state.caller_email
        and state.meeting_date
        and state.meeting_time
        and not state.meeting_purpose
        and not information.get("meeting_purpose")
        and not information.get("caller_email")
        and not information.get("caller_phone")
        and not information.get("date_value")
        and not information.get("time_text")
        and not information.get("caller_name")
    ):
        purpose = text.strip().rstrip(" .,!?")

        if (
            purpose
            and purpose.lower() not in blocked_purpose_answers
            and not contains_booking_intent(purpose)
            and len(purpose) <= 200
        ):
            information["meeting_purpose"] = purpose

    return information


def apply_local_information(
    information: dict,
    manager: ConversationManager,
):
    updates = {}

    if information.get("wants_meeting"):
        updates["meeting_requested"] = True

    for key in (
        "caller_name",
        "caller_email",
        "caller_phone",
        "meeting_purpose",
    ):
        if information.get(key):
            updates[key] = information[key]

    if information.get("date_value"):
        updates["meeting_date"] = information["date_value"]

    if information.get("time_text"):
        updates["meeting_time"] = information["time_text"]

    if updates:
        manager.update(**updates)


def extract_information(
    user_message: str,
    manager: ConversationManager,
) -> dict:
    state = manager.get_state()
    history = manager.get_history()[-8:]

    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history
    )

    prompt = f"""
You are the natural-language understanding layer of a professional
AI receptionist.

Extract only information clearly stated or implied by the latest message.
Do not invent information.

CURRENT STATE
Caller name: {state.caller_name}
Caller email: {state.caller_email}
Caller phone: {state.caller_phone}
Meeting requested: {state.meeting_requested}
Meeting date: {state.meeting_date}
Meeting time: {state.meeting_time}
Meeting purpose: {state.meeting_purpose}
Awaiting confirmation: {state.awaiting_confirmation}

RECENT CONVERSATION
{history_text}

LATEST CALLER MESSAGE
{user_message}

Return ONLY valid JSON with these keys:
{{
  "intent": "booking | general | correction | confirmation | cancellation | unknown",
  "caller_name": null,
  "caller_email": null,
  "caller_phone": null,
  "date_text": null,
  "time_text": null,
  "meeting_purpose": null,
  "wants_meeting": false,
  "confirmation": null
}}

Rules:
- Extract only details explicitly stated or clearly implied.
- Do not invent names, emails, dates, times, or purposes.
- Set wants_meeting to true if the caller clearly wants a meeting.
- Identify answers to questions asked earlier in the conversation.
- Set confirmation to true for a clear affirmative booking confirmation.
- Set confirmation to false for a clear rejection.
- Return JSON only.
"""

    response = ask_gemini(prompt)

    if not response:
        return {}

    cleaned = response.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def apply_gemini_information(
    information: dict,
    manager: ConversationManager,
):
    updates = {}

    for key in (
        "caller_name",
        "caller_email",
        "caller_phone",
        "meeting_purpose",
    ):
        value = information.get(key)
        if isinstance(value, str) and value.strip():
            updates[key] = value.strip()

    if information.get("wants_meeting") is True:
        updates["meeting_requested"] = True

    date_text = information.get("date_text")
    if date_text:
        resolved = resolve_relative_date(
            date_text,
            reference_date=date.today(),
        )
        if resolved:
            updates["meeting_date"] = resolved

    time_text = information.get("time_text")
    if time_text:
        normalized = normalize_time(time_text)
        if normalized:
            updates["meeting_time"] = normalized

    if updates:
        manager.update(**updates)


def answer_general_question(
    user_message: str,
    manager: ConversationManager,
) -> str:
    company_context = build_context_prompt()
    contacts_context = build_contacts_prompt()

    history = manager.get_history()[-10:]

    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history
    )

    prompt = f"""
You are the AI receptionist for Agentic AI Solutions.

Have a natural, professional conversation.
Answer the caller's actual question first.
Do not behave like a form.
Remember information already provided.
Do not repeatedly ask for information already given.
Do not collect meeting details unless the caller wants a meeting.

{company_context}

{contacts_context}

RECENT CONVERSATION:
{history_text}

CALLER'S LATEST MESSAGE:
{user_message}

Respond naturally as a professional receptionist.
Never claim a meeting has been booked unless the scheduler
has successfully created it.
"""

    response = ask_gemini(prompt)

    if response:
        return response.strip()

    return (
        "I'm sorry, I wasn't able to process that right now. "
        "Could you please say that again?"
    )


def format_date_for_speech(date_value: str) -> str:
    try:
        parsed = datetime.strptime(date_value, "%Y-%m-%d")
        return parsed.strftime("%A, %B %d")
    except (ValueError, TypeError):
        return date_value


def format_time_for_speech(time_value: str) -> str:
    try:
        parsed = datetime.strptime(time_value, "%H:%M")
        return parsed.strftime("%I:%M %p").lstrip("0")
    except (ValueError, TypeError):
        return time_value


def handle_booking(manager: ConversationManager) -> str:
    state = manager.get_state()

    if not state.meeting_requested:
        manager.update(meeting_requested=True)
        state = manager.get_state()

    if not state.caller_name:
        return "Absolutely. May I have your name?"

    if not state.caller_email:
        return f"Nice to meet you, {state.caller_name}. Could I get your email address?"

    if not state.meeting_date:
        return "What day would you like to meet?"

    if not state.meeting_time:
        return "What time would work best for you?"

    if not state.meeting_purpose:
        return "And what would you like to discuss in the meeting?"

    valid, message = is_within_business_hours(
        state.meeting_date,
        state.meeting_time,
        state.meeting_duration,
    )

    readable_date = format_date_for_speech(state.meeting_date)
    readable_time = format_time_for_speech(state.meeting_time)

    if not valid:
        if "Monday to Friday" in message:
            return (
                f"{readable_date} is outside our meeting schedule. "
                "Meetings are available Monday through Friday. "
                "Would you like to choose another day?"
            )

        if "before 9:00 AM" in message:
            return (
                f"{readable_time} on {readable_date} is before our business hours. "
                "Meetings are available from 9:00 AM to 6:00 PM. "
                "What time would work instead?"
            )

        if "latest available meeting start time" in message:
            return (
                f"{readable_time} is outside our meeting hours. "
                "What time between 9:00 AM and 6:00 PM would work instead?"
            )

        return (
            f"{readable_time} on {readable_date} is not available. "
            "Could you choose another time?"
        )

    available = check_availability(
        state.meeting_date,
        state.meeting_time,
        state.meeting_duration,
    )

    if not available:
        alternatives = find_available_slots(
            state.meeting_date,
            state.meeting_duration,
        )

        if alternatives:
            readable = [
                format_time_for_speech(slot)
                for slot in alternatives[:4]
            ]

            if len(readable) > 1:
                slots_text = ", ".join(readable[:-1]) + f", or {readable[-1]}"
            else:
                slots_text = readable[0]

            return (
                f"I'm sorry, {readable_time} on {readable_date} is already booked. "
                f"I have these available times: {slots_text}. "
                "Would any of those work for you?"
            )

        return (
            f"There aren't any available meeting slots on {readable_date}. "
            "Would you like to try another day?"
        )

    if not state.awaiting_confirmation:
        manager.update(awaiting_confirmation=True)

        return (
            f"Just to confirm, you'd like to meet with Harsha on "
            f"{readable_date} at {readable_time} for "
            f"{state.meeting_purpose}. Shall I book that for you?"
        )

    return (
        f"Everything is ready for {readable_date} at {readable_time}. "
        "Shall I confirm the booking?"
    )


def is_positive_confirmation(text: str) -> bool:
    lowered = re.sub(r"\s+", " ", text.lower().strip())

    phrases = {
        "yes", "yeah", "yep", "yup", "yes please",
        "please do", "confirm", "confirmed", "go ahead",
        "okay", "ok", "sure", "that's fine", "that works",
        "book it", "please book", "please book it",
        "confirm it", "please confirm", "please confirm it",
        "you may book", "you may book it",
        "you may confirm", "you may confirm it",
        "you can book", "you can book it",
        "you can confirm", "you can confirm it",
    }

    if lowered in phrases:
        return True

    return bool(
        re.fullmatch(
            r"(yes|yeah|yep|yup)\s+(you|u)\s+(may|can)\s+"
            r"(book|confirm)(?:\s+it)?",
            lowered,
        )
    )


def is_negative_confirmation(text: str) -> bool:
    lowered = re.sub(r"\s+", " ", text.lower().strip())

    phrases = {
        "no", "nope", "not now", "cancel", "cancel it",
        "don't book", "do not book", "don't confirm",
        "do not confirm", "no thanks", "no thank you",
    }

    return lowered in phrases


def is_cancellation_request(text: str) -> bool:
    lowered = re.sub(r"\s+", " ", text.lower().strip())
    normalized = lowered.rstrip(" .!?,")

    phrases = {
        "cancel", "cancel it", "cancel this",
        "cancel the booking", "cancel my booking",
        "cancel this booking", "cancel the meeting",
        "cancel my meeting", "cancel this meeting",
        "cancel the appointment", "cancel my appointment",
        "stop booking", "stop the booking",
        "never mind", "nevermind", "forget it",
        "don't book", "do not book",
        "don't schedule", "do not schedule",
    }

    if normalized in phrases:
        return True

    return bool(
        re.search(
            r"\b(?:cancel|stop)\b.*\b(?:booking|meeting|appointment)\b",
            lowered,
        )
    )


def confirm_booking(manager: ConversationManager) -> str:
    """Save the appointment, then attempt an SMS without affecting the booking."""
    state = manager.get_state()

    if not manager.is_ready_for_confirmation():
        manager.update(awaiting_confirmation=False)
        return handle_booking(manager)

    result = create_appointment(
        name=state.caller_name,
        email=state.caller_email,
        phone=state.caller_phone,
        date=state.meeting_date,
        start_time=state.meeting_time,
        duration=state.meeting_duration,
        purpose=state.meeting_purpose,
    )

    if not result.get("success"):
        manager.update(awaiting_confirmation=False)

        alternatives = result.get("available_slots", [])

        if alternatives:
            readable = [
                format_time_for_speech(slot)
                for slot in alternatives[:4]
            ]

            slots_text = (
                ", ".join(readable[:-1]) + f", or {readable[-1]}"
                if len(readable) > 1
                else readable[0]
            )

            return (
                "That time has just been taken. "
                f"I have these alternatives available: {slots_text}. "
                "Would you like one of those?"
            )

        return (
            "I'm sorry, that time is no longer available. "
            "Would you like me to find another slot?"
        )

    # The appointment has been saved. Never undo it if SMS fails.
    manager.update(
        confirmed=True,
        awaiting_confirmation=False,
    )

    try:
        from app.sms_service import send_booking_confirmation

        sms_result = send_booking_confirmation(
            appointment=result,
            phone=result.get("phone") or state.caller_phone,
        )

        if sms_result.get("success"):
            logging.getLogger(__name__).info(
                "Booking confirmation SMS status: %s",
                sms_result.get("status", "unknown"),
            )
        else:
            logging.getLogger(__name__).warning(
                "Booking saved, but SMS was not sent: %s",
                sms_result.get("reason", "Unknown reason"),
            )
    except Exception:
        logging.getLogger(__name__).exception(
            "Booking was saved, but the SMS attempt failed."
        )

    return (
        f"You're all set, {state.caller_name}. "
        f"Your meeting with Harsha is booked for "
        f"{format_date_for_speech(state.meeting_date)} at "
        f"{format_time_for_speech(state.meeting_time)}. Thank you!"
    )


def get_upcoming_appointments(email: str) -> list:
    appointments = find_appointments_by_email(email)
    now = datetime.now()
    upcoming = []

    for appointment in appointments:
        try:
            appointment_datetime = datetime.strptime(
                f"{appointment[4]} {appointment[5]}",
                "%Y-%m-%d %H:%M",
            )
        except (ValueError, TypeError):
            continue

        if appointment_datetime > now:
            upcoming.append(appointment)

    return upcoming


def format_cancellation_appointment(appointment) -> str:
    readable_date = format_date_for_speech(appointment[4])
    readable_time = format_time_for_speech(appointment[5])
    purpose = appointment[8] or "your scheduled meeting"

    return (
        f"your meeting on {readable_date} at {readable_time}, "
        f"about {purpose}"
    )


def ask_cancellation_confirmation(
    appointment,
    manager: ConversationManager,
) -> str:
    manager.select_cancellation_appointment(int(appointment[0]))

    return (
        f"I found {format_cancellation_appointment(appointment)}. "
        "Would you like me to cancel this appointment? "
        "Please say yes to confirm or no to keep it."
    )


def select_cancellation_appointment(
    user_message: str,
    appointments: list,
):
    text = re.sub(r"\s+", " ", user_message.lower().strip())

    match = re.fullmatch(
        r"(?:appointment|option|number|the)?\s*#?(\d+)",
        text,
    )

    if match:
        index = int(match.group(1)) - 1

        if 0 <= index < len(appointments):
            return appointments[index]

    matches = []

    for appointment in appointments:
        try:
            parsed_date = datetime.strptime(appointment[4], "%Y-%m-%d")
        except (ValueError, TypeError):
            continue

        weekday = parsed_date.strftime("%A").lower()
        readable_date = format_date_for_speech(appointment[4]).lower()
        readable_time = format_time_for_speech(appointment[5]).lower()

        if (
            (readable_date in text or weekday in text)
            and readable_time in text
        ):
            matches.append(appointment)

    return matches[0] if len(matches) == 1 else None


def handle_existing_cancellation(
    user_message: str,
    manager: ConversationManager,
) -> str:
    state = manager.get_state()

    if state.awaiting_cancellation_confirmation:
        appointment_id = state.cancellation_appointment_id

        if appointment_id is None:
            manager.clear_cancellation()
            return "I couldn't identify the appointment. Please try again."

        if is_positive_confirmation(user_message):
            result = cancel_appointment(
                appointment_id=int(appointment_id),
                email=state.caller_email or "",
                confirmed=True,
            )

            manager.clear_cancellation()

            if result.get("success"):
                return (
                    "Your appointment has been cancelled successfully. "
                    f"It was scheduled for "
                    f"{format_date_for_speech(result['date'])} at "
                    f"{format_time_for_speech(result['start_time'])}. "
                    "Is there anything else I can help you with?"
                )

            return (
                "I couldn't cancel that appointment. "
                f"{result.get('message', 'Please try again.')}"
            )

        if is_negative_confirmation(user_message):
            manager.clear_cancellation()
            return (
                "Understood. I haven't cancelled your appointment. "
                "Your booking remains unchanged."
            )

        return (
            "I haven't cancelled anything yet. Please say yes to cancel "
            "the appointment, or no to keep it."
        )

    if state.cancellation_appointments:
        appointment = select_cancellation_appointment(
            user_message,
            state.cancellation_appointments,
        )

        if appointment is None:
            return "Please tell me the appointment number from the list."

        return ask_cancellation_confirmation(appointment, manager)

    email = extract_email(user_message) or state.caller_email

    if not email:
        return (
            "I can help cancel an existing appointment. "
            "What email address did you use when booking it?"
        )

    manager.update(caller_email=email)
    appointments = get_upcoming_appointments(email)

    if not appointments:
        manager.clear_cancellation()
        return (
            "I couldn't find any upcoming appointments associated with "
            "that email address. Please check the email address."
        )

    manager.update(cancellation_appointments=appointments)

    if len(appointments) == 1:
        return ask_cancellation_confirmation(appointments[0], manager)

    options = []

    for index, appointment in enumerate(appointments, start=1):
        options.append(
            f"{index}: {format_date_for_speech(appointment[4])} at "
            f"{format_time_for_speech(appointment[5])}, about "
            f"{appointment[8] or 'scheduled meeting'}"
        )

    return (
        f"I found {len(appointments)} upcoming appointments. "
        + ". ".join(options)
        + ". Which appointment would you like to cancel? "
        "Please tell me its number."
    )


def ask_agent(
    user_message: str,
    manager: ConversationManager,
) -> str:
    user_message = user_message.strip()

    if not user_message:
        return "How can I help you?"

    manager.add_message("user", user_message)
    state = manager.get_state()

    # Continue an existing cancellation workflow.
    if state.cancellation_requested:
        response = handle_existing_cancellation(user_message, manager)
        manager.add_message("assistant", response)
        return response

    # Detect a cancellation request.
    if is_cancellation_request(user_message):
        if (
            (state.meeting_requested or state.awaiting_confirmation)
            and not state.confirmed
        ):
            manager.update(
                meeting_requested=False,
                meeting_date=None,
                meeting_time=None,
                meeting_purpose=None,
                meeting_duration=30,
                awaiting_confirmation=False,
                confirmed=False,
            )

            response = (
                "No problem. I won't book it. "
                "Would you like to arrange a different meeting?"
            )

            manager.add_message("assistant", response)
            return response

        manager.start_cancellation()
        response = handle_existing_cancellation(user_message, manager)
        manager.add_message("assistant", response)
        return response

    # Extract and store details locally.
    local_info = extract_simple_booking_information(
        user_message,
        manager,
    )

    apply_local_information(local_info, manager)
    state = manager.get_state()

    # Handle a pending booking confirmation.
    if state.awaiting_confirmation:
        if is_positive_confirmation(user_message):
            response = confirm_booking(manager)
            manager.add_message("assistant", response)
            return response

        if is_negative_confirmation(user_message):
            manager.update(
                meeting_requested=False,
                meeting_date=None,
                meeting_time=None,
                meeting_purpose=None,
                meeting_duration=30,
                awaiting_confirmation=False,
                confirmed=False,
            )

            response = (
                "No problem. I won't book it. "
                "Would you like to arrange a different meeting?"
            )

            manager.add_message("assistant", response)
            return response

        # A new date or time means the caller is correcting the booking.
        correction_info = extract_simple_booking_information(
            user_message,
            manager,
        )

        if (
            correction_info.get("date_value")
            or correction_info.get("time_text")
        ):
            manager.update(awaiting_confirmation=False)
            apply_local_information(correction_info, manager)

            response = handle_booking(manager)
            manager.add_message("assistant", response)
            return response

    # Continue an existing or newly requested booking.
    if (
        local_info.get("wants_meeting") is True
        or state.meeting_requested
    ):
        response = handle_booking(manager)
        manager.add_message("assistant", response)
        return response

    # General questions use Gemini.
    response = answer_general_question(user_message, manager)
    manager.add_message("assistant", response)
    return response
