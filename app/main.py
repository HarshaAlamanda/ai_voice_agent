from app.agent import ask_agent
from app.conversation import ConversationManager


def print_banner():
    print()
    print("=" * 65)
    print("        AGENTIC AI SOLUTIONS - AI RECEPTIONIST")
    print("=" * 65)
    print()
    print("Type your message and press Enter.")
    print("Commands:")
    print("  /new   - Start a new caller session")
    print("  /state - Show current conversation state")
    print("  /quit  - Exit the receptionist")
    print()


def print_state(manager: ConversationManager):

    state = manager.get_state()

    print()
    print("--------------- CURRENT STATE ----------------")
    print(f"Caller Name       : {state.caller_name}")
    print(f"Caller Email      : {state.caller_email}")
    print(f"Caller Phone      : {state.caller_phone}")
    print(f"Meeting Requested : {state.meeting_requested}")
    print(f"Meeting Date      : {state.meeting_date}")
    print(f"Meeting Time      : {state.meeting_time}")
    print(f"Meeting Duration  : {state.meeting_duration} minutes")
    print(f"Meeting Purpose   : {state.meeting_purpose}")
    print(f"Awaiting Confirm  : {state.awaiting_confirmation}")
    print(f"Confirmed         : {state.confirmed}")
    print("-----------------------------------------------")
    print()


def main():

    print_banner()

    manager = ConversationManager()

    while True:

        try:

            user_input = input("You: ").strip()

        except (
            KeyboardInterrupt,
            EOFError
        ):

            print()
            print("Receptionist: Goodbye!")
            break

        if not user_input:

            continue

        # ----------------------------------------------------
        # Quit
        # ----------------------------------------------------

        if user_input.lower() in {
            "/quit",
            "quit",
            "exit"
        }:

            print()
            print("Receptionist: Thank you for calling. Goodbye!")
            break

        # ----------------------------------------------------
        # New caller
        # ----------------------------------------------------

        if user_input.lower() == "/new":

            manager.reset()

            print()
            print("------------------------------------------------")
            print("New caller session started.")
            print("------------------------------------------------")
            print()

            continue

        # ----------------------------------------------------
        # Show state
        # ----------------------------------------------------

        if user_input.lower() == "/state":

            print_state(
                manager
            )

            continue

        # ----------------------------------------------------
        # Send message to AI receptionist
        # ----------------------------------------------------

        try:

            response = ask_agent(
                user_input,
                manager
            )

            print()
            print(
                f"Receptionist: {response}"
            )
            print()

        except Exception as error:

            print()
            print(
                "Receptionist: I'm sorry, "
                "something went wrong while processing "
                "your request."
            )

            print()
            print(
                f"[Technical error: {error}]"
            )

            print()


if __name__ == "__main__":
    main()