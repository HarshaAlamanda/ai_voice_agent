import pytest

import app.scheduler as scheduler


@pytest.fixture(autouse=True)
def isolate_scheduler_database(tmp_path, monkeypatch):
    """
    Give each test its own temporary SQLite database.

    The real data/appointments.db file remains untouched.
    """
    test_database = tmp_path / "appointments_test.db"

    monkeypatch.setattr(
        scheduler,
        "DATABASE_FILE",
        test_database,
    )

    scheduler.initialize_database()

    yield