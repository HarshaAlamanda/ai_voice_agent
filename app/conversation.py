from dataclasses import dataclass, field
from typing import Optional


# ============================================================
# CONVERSATION STATE
# ============================================================

@dataclass
class ConversationState:

    # --------------------------------------------------------
    # Caller information
    # --------------------------------------------------------

    caller_name: Optional[str] = None

    caller_email: Optional[str] = None

    caller_phone: Optional[str] = None

    # --------------------------------------------------------
    # New appointment booking state
    # --------------------------------------------------------

    meeting_requested: bool = False

    meeting_date: Optional[str] = None

    meeting_time: Optional[str] = None

    meeting_duration: int = 30

    meeting_purpose: Optional[str] = None

    awaiting_confirmation: bool = False

    confirmed: bool = False

    # --------------------------------------------------------
    # Existing appointment cancellation state
    # --------------------------------------------------------

    cancellation_requested: bool = False

    awaiting_cancellation_confirmation: bool = False

    cancellation_appointment_id: Optional[int] = None

    cancellation_appointments: list = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Conversation history
    # --------------------------------------------------------

    conversation_history: list = field(
        default_factory=list
    )


# ============================================================
# CONVERSATION MANAGER
# ============================================================

class ConversationManager:

    def __init__(self):

        self.state = ConversationState()

    # --------------------------------------------------------
    # Conversation history
    # --------------------------------------------------------

    def add_message(
        self,
        role: str,
        content: str
    ):

        self.state.conversation_history.append(
            {
                "role": role,
                "content": content
            }
        )

    def get_history(self):

        return self.state.conversation_history

    # --------------------------------------------------------
    # Update conversation state
    # --------------------------------------------------------

    def update(
        self,
        **values
    ):

        for key, value in values.items():

            if hasattr(self.state, key):

                setattr(
                    self.state,
                    key,
                    value
                )

    def get_state(self):

        return self.state

    # --------------------------------------------------------
    # Reset conversation state
    # --------------------------------------------------------

    def reset(self):

        self.state = ConversationState()

    # --------------------------------------------------------
    # Caller information checks
    # --------------------------------------------------------

    def has_caller_name(self):

        return bool(
            self.state.caller_name
        )

    def has_caller_email(self):

        return bool(
            self.state.caller_email
        )

    # --------------------------------------------------------
    # Booking information checks
    # --------------------------------------------------------

    def has_meeting_date(self):

        return bool(
            self.state.meeting_date
        )

    def has_meeting_time(self):

        return bool(
            self.state.meeting_time
        )

    def has_meeting_purpose(self):

        return bool(
            self.state.meeting_purpose
        )

    def is_ready_for_confirmation(self):

        return all(
            [
                self.state.caller_name,
                self.state.meeting_date,
                self.state.meeting_time,
                self.state.meeting_purpose
            ]
        )

    def get_missing_booking_information(self):

        missing = []

        if not self.state.caller_name:
            missing.append("name")

        if not self.state.caller_email:
            missing.append("email")

        if not self.state.meeting_date:
            missing.append("date")

        if not self.state.meeting_time:
            missing.append("time")

        if not self.state.meeting_purpose:
            missing.append("purpose")

        return missing

    # --------------------------------------------------------
    # Cancellation state checks
    # --------------------------------------------------------

    def is_cancellation_requested(self):

        return self.state.cancellation_requested

    def is_awaiting_cancellation_confirmation(self):

        return (
            self.state.awaiting_cancellation_confirmation
        )

    def has_cancellation_appointment(self):

        return (
            self.state.cancellation_appointment_id
            is not None
        )

    def get_cancellation_appointment_id(self):

        return self.state.cancellation_appointment_id

    def get_cancellation_appointments(self):

        return self.state.cancellation_appointments

    # --------------------------------------------------------
    # Start cancellation workflow
    # --------------------------------------------------------

    def start_cancellation(self):

        self.update(
            cancellation_requested=True,
            awaiting_cancellation_confirmation=False,
            cancellation_appointment_id=None,
            cancellation_appointments=[]
        )

    # --------------------------------------------------------
    # Select appointment for cancellation
    # --------------------------------------------------------

    def select_cancellation_appointment(
        self,
        appointment_id: int
    ):

        self.update(
            cancellation_appointment_id=appointment_id,
            awaiting_cancellation_confirmation=True
        )

    # --------------------------------------------------------
    # Clear cancellation state
    # --------------------------------------------------------

    def clear_cancellation(self):

        self.update(
            cancellation_requested=False,
            awaiting_cancellation_confirmation=False,
            cancellation_appointment_id=None,
            cancellation_appointments=[]
        )