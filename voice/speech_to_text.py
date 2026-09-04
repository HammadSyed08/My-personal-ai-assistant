import sounddevice as sd
import speech_recognition as sr


class SpeechToText:

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(
        self,
        duration=5,
        sample_rate=16000
    ):
        """
        Record audio using sounddevice and
        convert it to text using Google Speech Recognition.
        """

        print("\n🎤 Listening...")

        try:

            # Record microphone audio
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="int16"
            )

            # Wait until recording finishes
            sd.wait()

            print("🧠 Understanding...")

            # Convert NumPy audio data into SpeechRecognition AudioData
            audio_data = sr.AudioData(
                recording.tobytes(),
                sample_rate,
                2
            )

            # Convert speech → text
            text = self.recognizer.recognize_google(
                audio_data
            )

            text = text.strip()

            if text:

                print(f"🗣️ You said: {text}")

                return text

            return None

        except sr.UnknownValueError:

            print("❌ I couldn't understand what you said.")

            return None

        except sr.RequestError as error:

            print(
                f"❌ Speech recognition service error: {error}"
            )

            return None

        except Exception as error:

            print(
                f"❌ Microphone error: {error}"
            )

            return None


speech_to_text = SpeechToText()