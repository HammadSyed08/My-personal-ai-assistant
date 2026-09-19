import sounddevice as sd
import speech_recognition as sr
import soundfile as sf
import numpy as np


def normalize_speech(text):
    """
    Normalize common speech-recognition mistakes
    before sending commands to HAMMU.
    """

    replacements = {
        "ammu": "hammu",
        "ham": "hammu",
        "hamu": "hammu",
        "hanu": "hammu",
        "hamen": "hammu",
        "han": "hammu",
        "ammu": "hammu",
        "ham hun": "hammu",
        "ham munh": "hammu",
        "ham moon": "hammu",
        "home screenshot": "hammu screenshot",
    }

    normalized = text.strip().lower()

    for wrong, correct in replacements.items():
        normalized = normalized.replace(
            wrong,
            correct
        )

    return normalized

class SpeechToText:

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(
        self,
        duration=5,
        sample_rate=48000
    ):
        """
        Record audio using sounddevice and
        convert it to text using Google Speech Recognition.
        """

        print("\n🎤 Listening...")

        try:

            # Record microphone audio until silence
            # Record microphone audio until silence
            print("🎤 Speak now...")

            audio_chunks = []

            silence_limit = 1.2
            block_duration = 0.1
            block_size = int(block_duration * sample_rate)

            silence_time = 0
            started_speaking = False


            def callback(indata, frames, time, status):
                audio_chunks.append(indata.copy())


            with sd.InputStream(
                device=15,
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
                blocksize=block_size,
                callback=callback
            ):
                processed_chunks = 0

                while True:

                    if len(audio_chunks) > processed_chunks:

                        chunk = audio_chunks[processed_chunks]
                        processed_chunks += 1

                        volume = np.abs(chunk).mean() * 32767

                        # print(f"🔊 Volume: {volume:.0f}")

                        if volume > 500:
                            started_speaking = True
                            silence_time = 0

                        elif started_speaking:
                            silence_time += block_duration

                        if started_speaking and silence_time >= silence_limit:
                            break

            recording = np.concatenate(audio_chunks, axis=0)

            # sf.write("debug_voice.wav", recording, sample_rate)
            # print("💾 Debug recording saved as debug_voice.wav")

            print("🧠 Understanding...")

            # Convert NumPy audio data into SpeechRecognition AudioData
            recording_int16 = np.clip(recording, -1.0, 1.0)
            recording_int16 = (recording_int16 * 32767).astype(np.int16)

            audio_data = sr.AudioData(
                recording_int16.tobytes(),
                sample_rate,
                2
            )

            # Convert speech → text
        #     text = self.recognizer.recognize_google(
        #         audio_data
        #     )

        #     text = text.strip()

        #     if text:

        #         text = normalize_speech(text)
        #         print(f"🗣️ You said: {text}")

        #         return text

        #     return None

        # except sr.UnknownValueError:

        #     print("❌ I couldn't understand what you said.")

        #     return None

            results = self.recognizer.recognize_google(
                audio_data,
                show_all=True
            )

            alternatives = results.get("alternative", [])

            if alternatives:
                print("\n🎯 Google alternatives:")
                for i, alternative in enumerate(alternatives):
                    print(f"{i + 1}. {alternative['transcript']}")

                text = alternatives[0]["transcript"].strip()
            else:
                return None

            text = normalize_speech(text)

            if text:
                print(f"🗣️ You said: {text}")
                return text

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