import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "appointments.db"
)


# ============================================================
# BUSINESS RULES
# ============================================================

BUSINESS_START = "09:00"
BUSINESS_END = "18:00"

# Latest possible meeting START depends on duration.
# The validation function ensures the meeting finishes
# no later than BUSINESS_END.

LATEST_MEETING_START = "18:00"

DEFAULT_DURATION = 30


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a SQLite database connection.
    """

    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(
        DATABASE_FILE
    )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():
    """
    Create the appointments table if it does not already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT,

            phone TEXT,

            date TEXT NOT NULL,

            start_time TEXT NOT NULL,

            end_time TEXT NOT NULL,

            duration INTEGER NOT NULL,

            purpose TEXT,

            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()

    connection.close()


# ============================================================
# DATE / TIME HELPERS
# ============================================================

def parse_datetime(
    date: str,
    time: str
) -> datetime:
    """
    Convert:

        date = 2026-09-24
        time = 18:00

    into a Python datetime object.
    """

    return datetime.strptime(
        f"{date} {time}",
        "%Y-%m-%d %H:%M"
    )


# ============================================================
# BUSINESS HOURS VALIDATION
# ============================================================

def is_within_business_hours(
    date: str,
    start_time: str,
    duration: int
):
    """
    Validate whether a meeting fits completely within
    the allowed business hours.

    Business days:
        Monday - Friday

    Business hours:
        09:00 - 18:00

    The meeting must START at or after 09:00
    and END at or before 18:00.

    Returns:

        (True, message)

    or:

        (False, message)
    """

    try:

        start = parse_datetime(
            date,
            start_time
        )

    except ValueError:

        return (
            False,
            "Invalid date or time format."
        )

    if duration <= 0:

        return (
            False,
            "Meeting duration must be greater than zero."
        )

    # Monday = 0
    # Sunday = 6

    if start.weekday() >= 5:

        return (
            False,
            "Meetings are available Monday to Friday only."
        )

    business_start = parse_datetime(
        date,
        BUSINESS_START
    )

    business_end = parse_datetime(
        date,
        BUSINESS_END
    )

    # Too early

    if start < business_start:

        return (
            False,
            "Meetings cannot start before 9:00 AM."
        )

    # Calculate meeting end time

    end = (
        start
        + timedelta(minutes=duration)
    )

    # Meeting must finish by 6:00 PM

    if end > business_end:

        return (
            False,
            "The meeting must finish by 6:00 PM."
        )

    return (
        True,
        "Meeting time is within the allowed schedule."
    )


# ============================================================
# GET APPOINTMENTS
# ============================================================

def get_appointments(
    date: str | None = None
):
    """
    Return appointments.

    If date is provided:
        Return appointments for that date.

    Otherwise:
        Return all appointments.
    """

    connection = get_connection()

    cursor = connection.cursor()

    if date:

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                date,
                start_time,
                end_time,
                duration,
                purpose,
                created_at
            FROM appointments
            WHERE date = ?
            ORDER BY start_time
            """,
            (date,)
        )

    else:

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                date,
                start_time,
                end_time,
                duration,
                purpose,
                created_at
            FROM appointments
            ORDER BY date, start_time
            """
        )

    appointments = cursor.fetchall()

    connection.close()

    return appointments


# ============================================================
# CHECK AVAILABILITY
# ============================================================

def check_availability(
    date: str,
    start_time: str,
    duration: int = DEFAULT_DURATION
) -> bool:
    """
    Check whether a meeting slot is available.

    This function checks:

    1. Valid date/time
    2. Monday-Friday
    3. Meeting fits completely within business hours
    4. Existing appointment conflicts
    """

    valid, _ = is_within_business_hours(
        date,
        start_time,
        duration
    )

    if not valid:

        return False

    start = parse_datetime(
        date,
        start_time
    )

    end = (
        start
        + timedelta(minutes=duration)
    )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            start_time,
            end_time
        FROM appointments
        WHERE date = ?
        """,
        (date,)
    )

    existing_appointments = cursor.fetchall()

    connection.close()

    # Check for overlapping appointments

    for (
        existing_start,
        existing_end
    ) in existing_appointments:

        existing_start_dt = parse_datetime(
            date,
            existing_start
        )

        existing_end_dt = parse_datetime(
            date,
            existing_end
        )

        # Overlap formula:
        #
        # requested_start < existing_end
        # AND
        # requested_end > existing_start

        if (
            start < existing_end_dt
            and end > existing_start_dt
        ):

            return False

    return True


# ============================================================
# FIND AVAILABLE SLOTS
# ============================================================

def find_available_slots(
    date: str,
    duration: int = DEFAULT_DURATION,
    interval_minutes: int = 30
):
    """
    Find available meeting slots for a particular date.

    Example:

        09:00
        09:30
        10:00
        ...
        18:00

    The function returns only slots that are actually available.
    """

    slots = []

    try:

        current_time = parse_datetime(
            date,
            BUSINESS_START
        )

        latest_start = parse_datetime(
            date,
            LATEST_MEETING_START
        )

    except ValueError:

        return slots

    while current_time <= latest_start:

        time_string = current_time.strftime(
            "%H:%M"
        )

        if check_availability(
            date,
            time_string,
            duration
        ):

            slots.append(
                time_string
            )

        current_time += timedelta(
            minutes=interval_minutes
        )

    return slots


# ============================================================
# CREATE APPOINTMENT
# ============================================================

def create_appointment(
    name: str,
    email: str | None,
    phone: str | None,
    date: str,
    start_time: str,
    duration: int,
    purpose: str
):
    """
    Create an appointment only if the requested slot is available.

    IMPORTANT:
        This function NEVER creates an overlapping appointment.
    """

    # --------------------------------------------------------
    # Validate business rules
    # --------------------------------------------------------

    valid, message = is_within_business_hours(
        date,
        start_time,
        duration
    )

    if not valid:

        return {
            "success": False,
            "message": message
        }

    # --------------------------------------------------------
    # Check availability
    # --------------------------------------------------------

    if not check_availability(
        date,
        start_time,
        duration
    ):

        available_slots = find_available_slots(
            date,
            duration
        )

        return {
            "success": False,
            "message": "That time is already booked.",
            "available_slots": available_slots[:5]
        }

    # --------------------------------------------------------
    # Calculate end time
    # --------------------------------------------------------

    start = parse_datetime(
        date,
        start_time
    )

    end = (
        start
        + timedelta(minutes=duration)
    )

    end_time = end.strftime(
        "%H:%M"
    )

    # --------------------------------------------------------
    # Insert appointment
    # --------------------------------------------------------

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO appointments (
            name,
            email,
            phone,
            date,
            start_time,
            end_time,
            duration,
            purpose,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            email,
            phone,
            date,
            start_time,
            end_time,
            duration,
            purpose,
            datetime.now().isoformat()
        )
    )

    connection.commit()

    appointment_id = cursor.lastrowid

    connection.close()

    # --------------------------------------------------------
    # Return booking confirmation data
    # --------------------------------------------------------

    return {
        "success": True,
        "appointment_id": appointment_id,
        "name": name,
        "email": email,
        "phone": phone,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
        "purpose": purpose
    }


# ============================================================
# INITIALIZE DATABASE
# ============================================================

initialize_database()
# ============================================================
# EXISTING APPOINTMENT CANCELLATION
# ============================================================

def find_appointments_by_email(email: str):
    """
    Find appointments associated with an email address.

    Returns appointment rows in the same format as get_appointments().
    """

    if not email or not email.strip():
        return []

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                date,
                start_time,
                end_time,
                duration,
                purpose,
                created_at
            FROM appointments
            WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))
            ORDER BY date, start_time
            """,
            (email.strip(),)
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_appointment_by_id(appointment_id: int):
    """
    Retrieve one appointment using its unique database ID.

    Returns the appointment row or None if it does not exist.
    """

    if not isinstance(appointment_id, int) or appointment_id <= 0:
        return None

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                date,
                start_time,
                end_time,
                duration,
                purpose,
                created_at
            FROM appointments
            WHERE id = ?
            """,
            (appointment_id,)
        )

        return cursor.fetchone()

    finally:
        connection.close()


def cancel_appointment(
    appointment_id: int,
    email: str,
    confirmed: bool = False
):
    """
    Cancel a specific appointment.

    Safety rules:
    - Explicit confirmation is required.
    - The appointment ID must exist.
    - The supplied email must match the appointment.
    - Only the selected appointment is deleted.

    Returns a dictionary describing the result.
    """

    if not confirmed:
        return {
            "success": False,
            "message": (
                "Cancellation requires explicit confirmation."
            )
        }

    if not email or not email.strip():
        return {
            "success": False,
            "message": "A valid booking email is required."
        }

    if not isinstance(appointment_id, int) or appointment_id <= 0:
        return {
            "success": False,
            "message": "Invalid appointment ID."
        }

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Verify the appointment ID and caller's email together.
        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                date,
                start_time,
                end_time,
                duration,
                purpose,
                created_at
            FROM appointments
            WHERE id = ?
              AND LOWER(TRIM(email)) = LOWER(TRIM(?))
            """,
            (appointment_id, email.strip())
        )

        appointment = cursor.fetchone()

        if appointment is None:
            return {
                "success": False,
                "message": (
                    "No matching appointment was found for "
                    "that appointment ID and email address."
                )
            }

        # Delete only the verified appointment.
        cursor.execute(
            """
            DELETE FROM appointments
            WHERE id = ?
              AND LOWER(TRIM(email)) = LOWER(TRIM(?))
            """,
            (appointment_id, email.strip())
        )

        if cursor.rowcount != 1:
            connection.rollback()

            return {
                "success": False,
                "message": (
                    "The appointment could not be cancelled."
                )
            }

        connection.commit()

        return {
            "success": True,
            "message": "Appointment cancelled successfully.",
            "appointment_id": appointment[0],
            "name": appointment[1],
            "email": appointment[2],
            "date": appointment[4],
            "start_time": appointment[5],
            "end_time": appointment[6],
            "purpose": appointment[8]
        }

    except sqlite3.Error:
        connection.rollback()

        return {
            "success": False,
            "message": (
                "A database error occurred while cancelling "
                "the appointment."
            )
        }

    finally:
        connection.close()