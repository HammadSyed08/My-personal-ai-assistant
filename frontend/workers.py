import sys
import os

# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from PySide6.QtCore import QObject, Signal, Slot

from core.command_engine import process_command
from voice.speech_to_text import speech_to_text
from speech_controller import speech_controller


# ---------------------------------------------------------
# Background workers
# ---------------------------------------------------------

class CommandWorker(QObject):

    command_received = Signal(str)
    finished = Signal(object)
    error = Signal(str)

    def __init__(self):
        super().__init__()

        self.command_received.connect(
            self.run
        )

    @Slot(str)
    def run(self, command):

        try:

            result = process_command(command)

            self.finished.emit(result)

        except Exception as error:

            self.error.emit(
                str(error)
            )


class VoiceWorker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def run(self):
        try:
            text = speech_to_text.listen()
            self.finished.emit(text)
        except Exception as error:
            self.error.emit(str(error))


# ---------------------------------------------------------
# Voice greeting worker
# ---------------------------------------------------------

class GreetingWorker(QObject):

    finished = Signal()
    error = Signal(str)

    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        try:
            speech_controller.speak(
                self.message
            )

            self.finished.emit()

        except Exception as error:
            self.error.emit(
                str(error)
            )


class SpeechWorker(QObject):
    speak_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.speak_requested.connect(self.run)

    @Slot(str)
    def run(self, text):
        try:
            if text:
                speech_controller.speak(text)

        except Exception as error:
            print(
                f"❌ Speech worker error: {error}"
            )
