import pyttsx3
import threading


class TextToSpeech:
    def __init__(self):
        self.rate = 175
        self.volume = 1.0
        self._lock = threading.Lock()

    def _create_engine(self):
        engine = pyttsx3.init()

        engine.setProperty("rate", self.rate)
        engine.setProperty("volume", self.volume)

        try:
            voices = engine.getProperty("voices")

            for voice in voices:
                voice_name = voice.name.lower()

                if "english" in voice_name or "zira" in voice_name:
                    engine.setProperty("voice", voice.id)
                    break

        except Exception as error:
            print(f"⚠️ Voice selection warning: {error}")

        return engine

    def speak(self, text):
        if not text:
            return

        text = " ".join(str(text).split())

        if not text:
            return

        with self._lock:
            engine = None

            try:
                print(f"🔊 HAMMU: {text}")

                # Create a fresh SAPI/pyttsx3 engine for every speech request.
                # This avoids the Windows pyttsx3 engine getting stuck
                # after a previous runAndWait().
                engine = self._create_engine()

                engine.say(text)
                engine.runAndWait()

            except Exception as error:
                print(f"❌ Text-to-speech error: {error}")

            finally:
                try:
                    if engine is not None:
                        engine.stop()
                except Exception:
                    pass


text_to_speech = TextToSpeech()