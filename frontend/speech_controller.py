import threading

from voice.text_to_speech import text_to_speech


class SpeechController:
    """
    Central controller for HAMMU text-to-speech.

    Ensures only one pyttsx3 speech operation runs at a time.
    """

    def __init__(self):
        self._lock = threading.Lock()

    def speak(self, text):
        if not text:
            return

        with self._lock:
            try:
                text = " ".join(text.split())

                if not text:
                    return

                print(f"🔊 HAMMU SPEAKING: {text}")

                text_to_speech.speak(text)

            except Exception as error:
                print(
                    f"❌ Speech controller error: {error}"
                )


speech_controller = SpeechController()