from app.date_resolver import normalize_time


def test_3_pm():
    assert normalize_time("3 PM") == "15:00"


def test_3_am():
    assert normalize_time("3 AM") == "03:00"


def test_330_pm():
    assert normalize_time("3:30 PM") == "15:30"


def test_330_am():
    assert normalize_time("3:30 AM") == "03:30"


def test_24_hour_time():
    assert normalize_time("15:00") == "15:00"


def test_morning_time():
    assert normalize_time("9 AM") == "09:00"


def test_noon():
    assert normalize_time("12 PM") == "12:00"


def test_midnight():
    assert normalize_time("12 AM") == "00:00"


def test_half_past():
    assert normalize_time("half past 3") == "03:30"


def test_quarter_past():
    assert normalize_time("quarter past 3") == "03:15"


def test_quarter_to():
    assert normalize_time("quarter to 4") == "03:45"