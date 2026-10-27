import json
from pathlib import Path


CONTACTS_FILE = (
    Path(__file__).resolve().parent.parent
    / "knowledge"
    / "contacts.json"
)


def load_contacts() -> dict:
    """Load company contacts."""

    if not CONTACTS_FILE.exists():
        raise FileNotFoundError(
            f"Contacts file not found: {CONTACTS_FILE}"
        )

    with CONTACTS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_owner() -> dict:
    """Return owner information."""

    contacts = load_contacts()

    return contacts["owner"]


def get_general_email() -> str:
    """Return the company's general email."""

    contacts = load_contacts()

    return contacts["company_contacts"]["general_email"]


def get_department(department: str) -> dict | None:
    """Return information for a department."""

    contacts = load_contacts()

    departments = contacts.get(
        "departments",
        {}
    )

    return departments.get(department)


def build_contacts_prompt() -> str:
    """Create a safe prompt section for Gemini."""

    contacts = load_contacts()

    owner = contacts["owner"]
    company = contacts["company_contacts"]

    return f"""
CONTACT INFORMATION

Owner:
{owner["name"]}

Role:
{owner["role"]}

Owner availability:
{owner["availability"]}

General company email:
{company["general_email"]}

Contact rules:
{chr(10).join("- " + rule for rule in contacts["rules"])}
""".strip()