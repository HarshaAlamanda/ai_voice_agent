
"""SMS confirmation service for the Agentic AI receptionist.

Mock mode formats and simulates SMS delivery without contacting a provider.
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

BUSINESS_NAME = "Agentic AI Solutions"
SUPPORT_EMAIL = "agenticai.support@gmail.com"


def build_booking_confirmation(appointment: dict[str, Any]) -> str:
    """Build an SMS using the saved appointment details."""

    appointment_id = (
        appointment.get("appointment_id")
        or appointment.get("id")
    )
    if appointment_id is None:
        raise ValueError("Appointment ID is required for confirmation.")

    name = appointment.get("name") or "Customer"
    meeting_date = appointment.get("date") or "Not specified"
    meeting_time = appointment.get("start_time") or "Not specified"
    duration = appointment.get("duration") or 30
    purpose = appointment.get("purpose") or "Meeting"

    return (
        f"Your meeting with {BUSINESS_NAME} is booked. "
        f"Date: {meeting_date}; Time: {meeting_time} IST; "
        f"Duration: {duration} minutes; Purpose: {purpose}; "
        f"Reference: #{appointment_id}. "
        f"Help: {SUPPORT_EMAIL}"
    )


def send_booking_confirmation(
    appointment: dict[str, Any],
    phone: str | None = None,
) -> dict[str, Any]:
    """Simulate confirmation delivery without sending a real SMS."""

    recipient = phone or appointment.get("phone")

    if not recipient:
        return {
            "success": False,
            "status": "skipped",
            "reason": "No caller phone number is available.",
        }

    message = build_booking_confirmation(appointment)
    mode = os.getenv("SMS_MODE", "mock").strip().lower()

    if mode != "mock":
        logger.warning(
            "SMS mode %r is not implemented; no SMS was sent.",
            mode,
        )
        return {
            "success": False,
            "status": "not_sent",
            "reason": "Only mock mode is implemented.",
            "message": message,
        }

    logger.info(
        "MOCK SMS to %s: %s",
        _mask_phone(str(recipient)),
        message,
    )

    return {
        "success": True,
        "status": "mock_sent",
        "recipient": _mask_phone(str(recipient)),
        "message": message,
    }


def _mask_phone(phone: str) -> str:
    """Mask phone digits before logging or returning the recipient."""
    digits = "".join(character for character in phone if character.isdigit())
    if len(digits) <= 4:
        return "****"
    return f"****{digits[-4:]}"
