from core.command_engine import process_command
from voice.speech_to_text import speech_to_text
from security.permissions import set_confirmation_mode

# ============================================================
# Voice MODE
# ============================================================

def run_voice_mode():

    print("\n" + "=" * 50)
    print("🎤 HAMMU VOICE MODE")
    print("=" * 50)

    print("Say your command.")
    print("Say 'exit voice mode' to return to keyboard mode.")

    while True:

        text = speech_to_text.listen()

        # Nothing recognized
        if not text:
            continue

        # Check for voice-mode exit
        if text.lower().strip() in [
            "exit voice",
            "exit voice mode",
            "quit voice",
            "quit voice mode",
            "stop voice",
            "stop voice mode",
            "keyboard mode"
        ]:
            print("\n⌨️ Returning to keyboard mode...")
            break

        # Send voice text to the SAME command engine
        print(f"⚙️ Processing: {text}")
        result = process_command(text)

        if result["type"] == "chat":
            print(
                "\nAssistant:",
                result.get("response", "")
            )

        elif result["type"] == "tool":
            print(
                "\nAssistant:",
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
                "\nAssistant:",
                result.get(
                    "response",
                    "Something went wrong."
                )
            )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    set_confirmation_mode("terminal")

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
            "stop",
            "close hammu",
            "exit hammu",
            "quit hammu",
            "stop hammu",
        ]:

            print("Assistant: Goodbye!")
            break

        if user_input.lower() == "voice":
            run_voice_mode()
            continue

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