import threading
from voice.text_to_speech import text_to_speech


class SpeechController:
    """
    Centralized HAMMU text-to-speech controller.

    Only one speech operation can run at a time.
    """

    def __init__(self):
        self._lock = threading.Lock()

    def speak(self, text):
        if not text:
            return

        text = " ".join(str(text).split())

        if not text:
            return

        with self._lock:
            try:
                print(f"🔊 HAMMU SPEAKING: {text}")
                text_to_speech.speak(text)

            except Exception as error:
                print(f"❌ Speech controller error: {error}")


speech_controller = SpeechController()