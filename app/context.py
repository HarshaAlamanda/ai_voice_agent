import json
from pathlib import Path


CONTEXT_FILE = (
    Path(__file__).resolve().parent.parent
    / "knowledge"
    / "company_context.json"
)


def load_context() -> dict:
    """Load the company knowledge from company_context.json."""

    if not CONTEXT_FILE.exists():
        raise FileNotFoundError(
            f"Company context file not found: {CONTEXT_FILE}"
        )

    with CONTEXT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_company_name() -> str:
    """Return the company name."""

    context = load_context()

    return context["company_name"]


def get_company_context() -> dict:
    """Return the complete company context."""

    return load_context()


def build_context_prompt() -> str:
    """
    Convert the company context into a structured prompt
    that Gemini can use when answering caller questions.
    """

    context = load_context()

    services = "\n".join(
        f"- {service}"
        for service in context["services"]
    )

    business_hours = "\n".join(
        f"- {day.capitalize()}: {hours}"
        for day, hours in context["business_hours"].items()
    )

    rules = "\n".join(
        f"- {rule}"
        for rule in context["receptionist_rules"]
    )

    return f"""
COMPANY INFORMATION

Company:
{context["company_name"]}

Description:
{context["description"]}

Services:
{services}

Business Hours:
{business_hours}

Location:
{context["location"]}

Contact Email:
{context["contact_email"]}

Meeting Policy:
- Default duration: {context["meeting_policy"]["default_duration_minutes"]} minutes
- Minimum duration: {context["meeting_policy"]["minimum_duration_minutes"]} minutes
- Maximum duration: {context["meeting_policy"]["maximum_duration_minutes"]} minutes


RECEPTIONIST RULES

{rules}
""".strip()