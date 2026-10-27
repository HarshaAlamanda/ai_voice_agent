from datetime import date, timedelta

from app.date_resolver import resolve_relative_date


def test_today():
    result = resolve_relative_date("today")

    assert result == date.today().strftime("%Y-%m-%d")


def test_tomorrow():
    result = resolve_relative_date("tomorrow")

    expected = date.today() + timedelta(days=1)

    assert result == expected.strftime("%Y-%m-%d")


def test_day_after_tomorrow():
    result = resolve_relative_date("day after tomorrow")

    expected = date.today() + timedelta(days=2)

    assert result == expected.strftime("%Y-%m-%d")


def test_tomorrow_case_insensitive():
    result = resolve_relative_date("Tomorrow")

    expected = date.today() + timedelta(days=1)

    assert result == expected.strftime("%Y-%m-%d")


def test_monday():
    result = resolve_relative_date("Monday")

    assert result is not None
    assert date.fromisoformat(result).weekday() == 0


def test_thursday():
    result = resolve_relative_date("Thursday")

    assert result is not None
    assert date.fromisoformat(result).weekday() == 3


def test_next_monday():
    result = resolve_relative_date("next Monday")

    assert result is not None
    assert date.fromisoformat(result).weekday() == 0


def test_coming_thursday():
    result = resolve_relative_date("coming Thursday")

    assert result is not None
    assert date.fromisoformat(result).weekday() == 3


def test_weekday_result_is_valid_iso_date():
    result = resolve_relative_date("Friday")

    assert result is not None

    parsed = date.fromisoformat(result)

    assert parsed.weekday() == 4