import pyttsx3


class TextToSpeech:

    def __init__(self):
        self.engine = pyttsx3.init()

        # Speech settings
        self.engine.setProperty("rate", 175)
        self.engine.setProperty("volume", 1.0)

        # Try to select a natural English voice
        self._configure_voice()

    def _configure_voice(self):
        try:
            voices = self.engine.getProperty("voices")

            for voice in voices:
                voice_name = voice.name.lower()

                if "english" in voice_name or "zira" in voice_name:
                    self.engine.setProperty(
                        "voice",
                        voice.id
                    )
                    break

        except Exception as error:
            print(
                f"⚠️ Voice selection warning: {error}"
            )

    def speak(self, text):
        if not text:
            return

        try:
            text = " ".join(text.split())

            print(f"🔊 HAMMU: {text}")

            self.engine.say(text)
            self.engine.runAndWait()

        except Exception as error:
            print(
                f"❌ Text-to-speech error: {error}"
            )


text_to_speech = TextToSpeech()