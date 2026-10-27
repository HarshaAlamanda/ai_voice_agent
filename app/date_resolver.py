from datetime import date, datetime, timedelta
import re


# ============================================================
# TIME NORMALIZATION
# ============================================================

def normalize_time(
    time_text: str
) -> str | None:
    """
    Convert common spoken time formats into HH:MM.

    Supported examples:
        6 PM           -> 18:00
        6:30 PM        -> 18:30
        9 AM           -> 09:00
        12 PM          -> 12:00
        12 AM          -> 00:00
        18:30          -> 18:30
        half past 3    -> 03:30
        quarter past 3 -> 03:15
        quarter to 4   -> 03:45
        3 o'clock      -> 03:00

    Expressions without AM/PM use the stated hour as written.
    """

    if not time_text:
        return None

    text = time_text.strip().lower()

    # Normalize punctuation and whitespace.
    text = re.sub(r"[,.?!]+$", "", text).strip()
    text = re.sub(r"\s+", " ", text)

    # --------------------------------------------------------
    # SPOKEN TIME EXPRESSIONS
    # --------------------------------------------------------

    spoken_match = re.fullmatch(
        r"(half past|quarter past|quarter to)\s+(\d{1,2})",
        text
    )

    if spoken_match:
        expression = spoken_match.group(1)
        hour = int(spoken_match.group(2))

        if not 1 <= hour <= 12:
            return None

        if expression == "half past":
            minute = 30

        elif expression == "quarter past":
            minute = 15

        else:
            minute = 45
            hour -= 1

            if hour == 0:
                hour = 12

        return f"{hour:02d}:{minute:02d}"

    # --------------------------------------------------------
    # O'CLOCK EXPRESSIONS
    # --------------------------------------------------------

    oclock_match = re.fullmatch(
        r"(\d{1,2})\s*(?:o['’]?clock|oclock)",
        text
    )

    if oclock_match:
        hour = int(oclock_match.group(1))

        if not 1 <= hour <= 12:
            return None

        return f"{hour:02d}:00"

    # --------------------------------------------------------
    # 24-HOUR FORMAT
    # --------------------------------------------------------

    match = re.fullmatch(
        r"(\d{1,2}):(\d{2})",
        text
    )

    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))

        if (
            0 <= hour <= 23
            and 0 <= minute <= 59
        ):
            return f"{hour:02d}:{minute:02d}"

        return None

    # --------------------------------------------------------
    # 12-HOUR FORMAT WITH AM/PM
    # --------------------------------------------------------

    match = re.fullmatch(
        r"(\d{1,2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?)",
        text
    )

    if match:
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        meridiem = match.group(3).replace(".", "")

        if not 1 <= hour <= 12:
            return None

        if not 0 <= minute <= 59:
            return None

        # Convert AM to 24-hour time.
        if meridiem == "am":
            if hour == 12:
                hour = 0

        # Convert PM to 24-hour time.
        else:
            if hour != 12:
                hour += 12

        return f"{hour:02d}:{minute:02d}"

    return None


# ============================================================
# NEXT WEEKDAY
# ============================================================

def next_weekday(
    target_weekday: int,
    reference_date: date
) -> date:
    """
    Return the next occurrence of a weekday.

    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6

    If the requested weekday is today,
    return the following week's occurrence.
    """

    days_ahead = (
        target_weekday
        - reference_date.weekday()
    ) % 7

    if days_ahead == 0:
        days_ahead = 7

    return (
        reference_date
        + timedelta(days=days_ahead)
    )


# ============================================================
# UPCOMING WEEKDAY
# ============================================================

def upcoming_weekday(
    target_weekday: int,
    reference_date: date
) -> date:
    """
    Return today's date if the weekday is today.

    Otherwise return the next occurrence.

    Examples:
        Thursday -> today, if today is Thursday
        Friday -> tomorrow, if today is Thursday
        Wednesday -> next Wednesday, if today is Thursday
    """

    days_ahead = (
        target_weekday
        - reference_date.weekday()
    ) % 7

    return (
        reference_date
        + timedelta(days=days_ahead)
    )


# ============================================================
# RESOLVE RELATIVE DATE
# ============================================================

def resolve_relative_date(
    text: str,
    reference_date: date | None = None
) -> str | None:
    """
    Resolve natural date expressions into YYYY-MM-DD.

    Supported examples:
        today
        tomorrow
        day after tomorrow
        Monday
        Thursday
        coming Thursday
        next Thursday
        this Thursday
        next week Thursday
        Thursday next week
        2026-09-24
        24-09-2026
        24/09/2026
    """

    if not text:
        return None

    if reference_date is None:
        reference_date = date.today()

    text = text.strip().lower()

    # --------------------------------------------------------
    # REMOVE TRAILING PUNCTUATION
    # --------------------------------------------------------

    text = text.rstrip(
        ".,?!"
    ).strip()

    # --------------------------------------------------------
    # TODAY
    # --------------------------------------------------------

    if text in {
        "today",
        "this day"
    }:
        return reference_date.isoformat()

    # --------------------------------------------------------
    # TOMORROW
    # --------------------------------------------------------

    if text in {
        "tomorrow",
        "tmrw",
        "tommorow"
    }:
        return (
            reference_date
            + timedelta(days=1)
        ).isoformat()

    # --------------------------------------------------------
    # DAY AFTER TOMORROW
    # --------------------------------------------------------

    if text in {
        "day after tomorrow",
        "day after tmrw"
    }:
        return (
            reference_date
            + timedelta(days=2)
        ).isoformat()

    # --------------------------------------------------------
    # WEEKDAY MAPPING
    # --------------------------------------------------------

    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    # --------------------------------------------------------
    # NEXT WEEK THURSDAY
    # THURSDAY NEXT WEEK
    # --------------------------------------------------------

    match = re.fullmatch(
        r"(?:next\s+week\s+"
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        r"|"
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        r"\s+next\s+week)",
        text
    )

    if match:
        weekday_name = (
            match.group(1)
            or match.group(2)
        )

        weekday = weekdays[weekday_name]

        current_occurrence = upcoming_weekday(
            weekday,
            reference_date
        )

        return (
            current_occurrence
            + timedelta(days=7)
        ).isoformat()

    # --------------------------------------------------------
    # NEXT THURSDAY
    # --------------------------------------------------------

    match = re.fullmatch(
        r"next\s+"
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        text
    )

    if match:
        weekday = weekdays[match.group(1)]

        next_occurrence = next_weekday(
            weekday,
            reference_date
        )

        return next_occurrence.isoformat()

    # --------------------------------------------------------
    # COMING THURSDAY
    # --------------------------------------------------------

    match = re.fullmatch(
        r"coming\s+"
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        text
    )

    if match:
        weekday = weekdays[match.group(1)]

        upcoming = upcoming_weekday(
            weekday,
            reference_date
        )

        return upcoming.isoformat()

    # --------------------------------------------------------
    # THIS THURSDAY
    # --------------------------------------------------------

    match = re.fullmatch(
        r"this\s+"
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        text
    )

    if match:
        weekday = weekdays[match.group(1)]

        upcoming = upcoming_weekday(
            weekday,
            reference_date
        )

        return upcoming.isoformat()

    # --------------------------------------------------------
    # PLAIN WEEKDAY
    # --------------------------------------------------------

    if text in weekdays:
        weekday = weekdays[text]

        upcoming = upcoming_weekday(
            weekday,
            reference_date
        )

        return upcoming.isoformat()

    # --------------------------------------------------------
    # ISO DATE: YYYY-MM-DD
    # --------------------------------------------------------

    try:
        parsed = datetime.strptime(
            text,
            "%Y-%m-%d"
        ).date()

        return parsed.isoformat()

    except ValueError:
        pass

    # --------------------------------------------------------
    # DD-MM-YYYY
    # --------------------------------------------------------

    try:
        parsed = datetime.strptime(
            text,
            "%d-%m-%Y"
        ).date()

        return parsed.isoformat()

    except ValueError:
        pass

    # --------------------------------------------------------
    # DD/MM/YYYY
    # --------------------------------------------------------

    try:
        parsed = datetime.strptime(
            text,
            "%d/%m/%Y"
        ).date()

        return parsed.isoformat()

    except ValueError:
        pass

    return None