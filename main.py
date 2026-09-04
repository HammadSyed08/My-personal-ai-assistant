from core.command_engine import process_command

# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)
    print("Hammu AI Assistant")
    print("=" * 60)

    while True:

        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() in [
            "exit",
            "quit",
            "stop"
        ]:

            print("Assistant: Goodbye!")
            break

        result = process_command(user_input)

        if result["type"] == "chat":

            print(
                "Assistant:",
                result.get("response", "")
            )

        elif result["type"] == "tool":

            print(
                "Assistant:",
                result.get("result", "")
            )

        elif result["type"] == "plan":

            for item in result.get("results", []):

                print(
                    f"[{item.get('tool')}] "
                    f"{item.get('result')}"
                )

            print("Assistant: Task completed.")

        else:

            print(
                "Assistant:",
                result.get(
                    "response",
                    "Something went wrong."
                )
            )

# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()