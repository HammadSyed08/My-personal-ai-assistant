import html
import winsound


from PySide6.QtCore import (
    Qt,
    QTimer,
    QThread,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QFrame,
    QStackedWidget,
)

from workers import CommandWorker, VoiceWorker, GreetingWorker, SpeechWorker
from voice.text_to_speech import text_to_speech


# ---------------------------------------------------------
# HAMMU audio effects
# ---------------------------------------------------------

from audio import (
    STARTUP_SOUND,
    LISTEN_TICK_SOUND,
)


# ---------------------------------------------------------
# Futuristic HUD visualizer
# ---------------------------------------------------------

from voice_ui import VoiceVisualizer



class HAMMUWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.command_thread = QThread(self)
        self.command_worker = CommandWorker()

        self.command_worker.moveToThread(
        self.command_thread
    )

        self.command_worker.finished.connect(
            self.command_finished
        )

        self.command_worker.error.connect(
            self.command_error
        )

        self.command_thread.start()

        self.voice_thread = None
        self.voice_worker = None
        self.greeting_thread = None
        self.greeting_worker = None

        self.speech_thread = QThread(self)
        self.speech_worker = SpeechWorker()
        self.speech_worker.moveToThread(self.speech_thread)
        self.speech_thread.start()  
        # self.speech_finished_callback = None

        self.listening_tick_timer = QTimer(self)
        self.listening_tick_timer.timeout.connect(
            self.play_listening_tick
)

        self.command_origin = "text"
        self.processing = False
        self.closing = False


        self.setup_window()
        self.setup_ui()
        self.setup_connections()
        self.show_welcome_message()

        QTimer.singleShot(
          350,
          self.play_startup_sound
      )

    # -----------------------------------------------------
    # Window
    # -----------------------------------------------------

    def setup_window(self):
        self.setWindowTitle("HAMMU — Personal AI Assistant")
        self.resize(1200, 760)
        self.setMinimumSize(960, 640)

    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------

    def setup_ui(self):

        self.setStyleSheet("""
            QWidget {
                background: #02060b;
                color: #e7faff;
                font-family: "Segoe UI";
            }

            QFrame#Header {
                background: #07121a;
                border-bottom: 1px solid #163441;
            }

            QLabel#Brand {
                color: #dffcff;
                font-size: 25px;
                font-weight: 700;
                letter-spacing: 2px;
            }

            QLabel#Subtitle {
                color: #6f9aa7;
                font-size: 11px;
                letter-spacing: 2px;
            }

            QLabel#Status {
                color: #67e9ff;
                font-size: 12px;
                font-weight: 600;
                padding: 7px 13px;
                border: 1px solid #164d5d;
                border-radius: 12px;
                background: #06131a;
            }

            QTextEdit#Chat {
                background: #03080d;
                border: 1px solid #102b36;
                border-radius: 18px;
                padding: 18px;
                font-size: 14px;
            }

            QLineEdit#Input {
                background: #07131a;
                border: 1px solid #1a414d;
                border-radius: 16px;
                padding: 14px 16px;
                color: #e7faff;
                font-size: 14px;
            }

            QLineEdit#Input:focus {
                border: 1px solid #49dff5;
            }

            QPushButton {
                background: #071820;
                border: 1px solid #1c5665;
                border-radius: 14px;
                color: #cceff5;
                padding: 10px 18px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #0b2630;
                border: 1px solid #4ce2f7;
            }

            QPushButton:pressed {
                background: #10313b;
            }

            QPushButton:disabled {
                color: #46636c;
                border-color: #16303a;
            }

            QPushButton#MicButton {
                border-radius: 18px;
                font-size: 20px;
                min-width: 55px;
                max-width: 55px;
                min-height: 48px;
                max-height: 48px;
            }

            QPushButton#VoiceCoreButton {
                border-radius: 40px;
                min-width: 82px;
                max-width: 82px;
                min-height: 82px;
                max-height: 82px;
                font-size: 27px;
                background: #081d25;
                border: 2px solid #43e2f6;
            }

            QPushButton#VoiceCoreButton:hover {
                background: #0c2d38;
            }

            QLabel#VoiceTitle {
                color: #e5fdff;
                font-size: 22px;
                font-weight: 700;
                letter-spacing: 3px;
            }

            QLabel#VoiceState {
                color: #61e6fa;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 4px;
            }

            QLabel#VoiceHint {
                color: #5c818b;
                font-size: 11px;
                letter-spacing: 2px;
            }

            QLabel#VoiceTranscript {
                color: #a7cbd2;
                font-size: 13px;
                padding: 8px 25px;
            }

            QLabel#VoiceResponse {
                color: #e1f8fb;
                font-size: 13px;
                padding: 4px 25px;
            }

            QFrame#Activity {
                background: #061017;
                border: 1px solid #102e39;
                border-radius: 10px;
            }

            QLabel#ActivityText {
                color: #5f8791;
                font-size: 11px;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 18)
        root.setSpacing(12)

        # -------------------------------------------------
        # Main header
        # -------------------------------------------------

        self.header = QFrame()
        self.header.setObjectName("Header")
        self.header.setFixedHeight(66)

        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(18, 8, 18, 8)

        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(0)

        self.brand = QLabel("HAMMU")
        self.brand.setObjectName("Brand")

        self.subtitle = QLabel("PERSONAL AI ASSISTANT")
        self.subtitle.setObjectName("Subtitle")

        brand_layout.addWidget(self.brand)
        brand_layout.addWidget(self.subtitle)

        header_layout.addLayout(brand_layout)
        header_layout.addStretch()

        self.status_label = QLabel("● READY")
        self.status_label.setObjectName("Status")

        header_layout.addWidget(self.status_label)

        root.addWidget(self.header)

        # -------------------------------------------------
        # Pages
        # -------------------------------------------------

        self.pages = QStackedWidget()
        root.addWidget(self.pages, 1)

        self.chat_page = self.create_chat_page()
        self.voice_page = self.create_voice_page()

        self.pages.addWidget(self.chat_page)
        self.pages.addWidget(self.voice_page)


# ---------------------------------------------------------
# HAMMU sound effects
# ---------------------------------------------------------

    def play_startup_sound(self):

        try:

            winsound.PlaySound(
                STARTUP_SOUND,
                winsound.SND_FILENAME |
                winsound.SND_ASYNC
            )

        except Exception as error:

            print(
                f"Startup sound warning: {error}"
            )


    def play_listening_tick(self):

        try:

            winsound.PlaySound(
                LISTEN_TICK_SOUND,
                winsound.SND_FILENAME |
                winsound.SND_ASYNC
            )

        except Exception:
            pass
        
    # -----------------------------------------------------
    # Chat page
    # -----------------------------------------------------

    def create_chat_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.chat = QTextEdit()
        self.chat.setObjectName("Chat")
        self.chat.setReadOnly(True)

        layout.addWidget(self.chat, 1)

        # Activity bar
        activity = QFrame()
        activity.setObjectName("Activity")
        activity.setFixedHeight(34)

        activity_layout = QHBoxLayout(activity)
        activity_layout.setContentsMargins(12, 4, 12, 4)

        self.activity_text = QLabel("SYSTEM READY")
        self.activity_text.setObjectName("ActivityText")

        activity_layout.addWidget(self.activity_text)
        activity_layout.addStretch()

        self.activity_status = QLabel("LOCAL AI • VOICE • MEMORY")
        self.activity_status.setObjectName("ActivityText")

        activity_layout.addWidget(self.activity_status)

        layout.addWidget(activity)

        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.input = QLineEdit()
        self.input.setObjectName("Input")
        self.input.setPlaceholderText(
            "Talk to HAMMU..."
        )

        self.mic_button = QPushButton("🎙")
        self.mic_button.setObjectName("MicButton")
        self.mic_button.setToolTip(
            "Enter HAMMU voice mode"
        )

        self.send_button = QPushButton("SEND")

        input_layout.addWidget(self.input, 1)
        input_layout.addWidget(self.mic_button)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        return page

    # -----------------------------------------------------
    # Voice page
    # -----------------------------------------------------

    def create_voice_page(self):

        page = QWidget()

        outer = QVBoxLayout(page)
        outer.setContentsMargins(8, 4, 8, 4)
        outer.setSpacing(4)

        # Top voice HUD bar
        top = QHBoxLayout()

        title = QLabel("HAMMU // VOICE CORE")
        title.setObjectName("VoiceTitle")

        top.addWidget(title)
        top.addStretch()

        self.back_chat_button = QPushButton("CHAT")
        self.back_chat_button.setFixedWidth(85)

        top.addWidget(self.back_chat_button)

        outer.addLayout(top)

        # Visualizer
        self.visualizer = VoiceVisualizer()
        outer.addWidget(self.visualizer, 1)

        # State
        self.voice_state = QLabel("READY")
        self.voice_state.setObjectName("VoiceState")
        self.voice_state.setAlignment(Qt.AlignCenter)

        outer.addWidget(self.voice_state)

        # Transcript
        self.voice_transcript = QLabel(
            "Say something to HAMMU"
        )
        self.voice_transcript.setObjectName(
            "VoiceTranscript"
        )
        self.voice_transcript.setAlignment(Qt.AlignCenter)
        self.voice_transcript.setWordWrap(True)

        outer.addWidget(self.voice_transcript)

        # Response
        self.voice_response = QLabel("")
        self.voice_response.setObjectName(
            "VoiceResponse"
        )
        self.voice_response.setAlignment(Qt.AlignCenter)
        self.voice_response.setWordWrap(True)

        outer.addWidget(self.voice_response)

        # Core microphone
        mic_layout = QHBoxLayout()
        mic_layout.setAlignment(Qt.AlignCenter)

        self.voice_core_button = QPushButton("🎙")
        self.voice_core_button.setObjectName(
            "VoiceCoreButton"
        )
        self.voice_core_button.setToolTip(
            "Speak to HAMMU"
        )

        mic_layout.addWidget(self.voice_core_button)

        outer.addLayout(mic_layout)

        self.voice_hint = QLabel(
            "TAP THE CORE TO SPEAK"
        )
        self.voice_hint.setObjectName("VoiceHint")
        self.voice_hint.setAlignment(Qt.AlignCenter)

        outer.addWidget(self.voice_hint)

        return page

    # -----------------------------------------------------
    # Connections
    # -----------------------------------------------------

    def setup_connections(self):

        self.send_button.clicked.connect(
            self.send_message
        )

        self.input.returnPressed.connect(
            self.send_message
        )

        self.mic_button.clicked.connect(
            self.enter_voice_mode
        )

        self.voice_core_button.clicked.connect(
            self.start_voice_input
        )

        self.back_chat_button.clicked.connect(
            self.exit_voice_mode
        )

    # -----------------------------------------------------
    # Welcome
    # -----------------------------------------------------

    def show_welcome_message(self):

      self.add_message(
          "HAMMU",
          "Welcome to HAMMU AI Assistant. "
          "ChatBot is activated and ready to help you."
      )


    def greeting_finished(self):

        self.processing = False

        self.voice_transcript.setText(
            "Welcome to HAMMU, your Personal AI Assistant."
        )

        self.voice_response.setText(
            "Audio microphone is activated."
        )

        self.voice_hint.setText(
            "LISTENING FOR YOUR COMMAND..."
        )

        # Give the greeting a tiny cinematic pause
        QTimer.singleShot(
            350,
            self.start_voice_input
        )


    def greeting_error(self, error):

        print(
            f"Voice greeting warning: {error}"
        )

        self.processing = False

        QTimer.singleShot(
            150,
            self.start_voice_input
        )

    # -----------------------------------------------------
    # Chat helpers
    # -----------------------------------------------------

    def add_message(self, sender, message):

        message = html.escape(
            str(message)
        ).replace("\n", "<br>")

        if sender == "You":
            bubble_color = "#0b2832"
            border = "#1b5361"
            align = "right"
        else:
            bubble_color = "#07161d"
            border = "#153b47"
            align = "left"

        bubble = f"""
        <div align="{align}">
            <table cellpadding="0" cellspacing="0"
                   style="
                   background:{bubble_color};
                   border:1px solid {border};
                   border-radius:14px;
                   margin:7px;
                   ">
                <tr>
                    <td style="
                        padding:10px 13px;
                        color:#8bddea;
                        font-size:11px;
                        font-weight:bold;
                        ">
                        {html.escape(sender)}
                    </td>
                </tr>
                <tr>
                    <td style="
                        padding:0px 13px 12px 13px;
                        color:#e2f8fb;
                        font-size:14px;
                        ">
                        {message}
                    </td>
                </tr>
            </table>
        </div>
        """

        self.chat.append(bubble)

        scrollbar = self.chat.verticalScrollBar()
        scrollbar.setValue(
            scrollbar.maximum()
        )

    def normalize_result(self, result):

        if not isinstance(result, dict):
            return str(result)

        if result.get("type") == "chat":
            response = result.get("response")
            if response:
                return str(response)

        tool = result.get("tool")
        value = result.get("result")

        if tool == "open_website" and isinstance(value, str):
            if value.lower().startswith("opened ") and value.endswith("."):
                return value[7:-1].capitalize() + " is open."
            return value

        if tool == "open_url" and isinstance(value, dict):
            if value.get("success"):
                url = str(value.get("url") or "").lower()
                if "google.com" in url:
                    return "Google is open."
                if url:
                    return "The website is open."

        if tool == "google_search" and isinstance(value, dict):
            if value.get("success"):
                count = value.get("count", 0)
                query = value.get("query", "")
                return f"I found {count} result(s) for {query}."

        if result.get("type") == "plan":
            results = result.get("results", [])
            if results:
                successful = sum(
                    1 for item in results
                    if isinstance(item, dict) and item.get("result") is not None
                )
                return f"I've completed the requested task. {successful} action(s) finished."

        for key in (
            "response",
            "result",
            "message",
            "error",
        ):
            value = result.get(key)
            if value not in (None, ""):
                if isinstance(value, dict):
                    if value.get("message"):
                        return str(value["message"])
                    if value.get("error"):
                        return str(value["error"])
                return str(value)

        return "HAMMU completed the command."

    def speak_async(self, text, callback=None):
      if not text:
          if callback:
              callback()
          return

      print(f"🔊 HAMMU SPEAKING: {text}")

      def speak_and_continue():
          try:
              from speech_controller import speech_controller

              speech_controller.speak(text)

          finally:
              if callback:
                  QTimer.singleShot(0, callback)

      QTimer.singleShot(0, speak_and_continue)

      def speak_and_continue():
          text_to_speech.speak(text)

          if callback:
              QTimer.singleShot(0, callback)

      QTimer.singleShot(0, speak_and_continue)
    # def speak_async(self, text, callback=None):

    #     if self.closing or not text:
    #         if callback:
    #             callback()
    #         return

    #     if self.speech_thread is not None and self.speech_thread.isRunning():
    #         if callback:
    #             QTimer.singleShot(0, callback)
    #         return

    #     self.speech_finished_callback = callback

    #     # Keep the QThread object alive after it finishes.
    #     # Deleting it here can leave a stale PySide6 wrapper, causing:
    #     # RuntimeError: Internal C++ object (QThread) already deleted
    #     self.speech_thread = QThread(self)
    #     self.speech_worker = SpeechWorker(text)
    #     self.speech_worker.moveToThread(self.speech_thread)

    #     self.speech_thread.started.connect(self.speech_worker.run)
    #     self.speech_worker.finished.connect(self.speech_finished)
    #     self.speech_worker.error.connect(self.speech_error)
    #     self.speech_worker.finished.connect(self.speech_thread.quit)
    #     self.speech_worker.error.connect(self.speech_thread.quit)
    #     self.speech_thread.finished.connect(self.speech_worker.deleteLater)

    #     self.speech_thread.start()

    # @Slot()
    # def speech_finished(self):
    #     callback = self.speech_finished_callback
    #     self.speech_finished_callback = None
    #     if callback:
    #         callback()

    # @Slot(str)
    # def speech_error(self, error):
    #     print(f"Speech communication warning: {error}")
    #     callback = self.speech_finished_callback
    #     self.speech_finished_callback = None
    #     if callback:
    #         callback()

    # -----------------------------------------------------
    # Text command
    # -----------------------------------------------------

    def send_message(self):

        if self.processing:
            return

        text = self.input.text().strip()

        if not text:
            return

        self.input.clear()

        self.add_message("You", text)

        self.command_origin = "text"

        self.set_processing_state(
            "THINKING",
            "PROCESSING COMMAND..."
        )

        self.start_command_worker_with_ack(
            text,
            "Got it. I'm working on that."
        )

    def closeEvent(self, event):

        self.closing = True

        try:
            # Stop accepting new commands.
            self.processing = True

            # Stop the permanent command worker thread.
            if self.command_thread.isRunning():
                self.command_thread.quit()
                self.command_thread.wait(3000)

            if self.speech_thread is not None and self.speech_thread.isRunning():
                self.speech_thread.quit()
                self.speech_thread.wait(1000)

        except Exception as error:

            print(
                f"Command thread shutdown warning: {error}"
            )

        event.accept()

    # -----------------------------------------------------
    # Command worker
    # -----------------------------------------------------

    def start_command_worker_with_ack(self, command, acknowledgement):
      self.processing = True

      self.send_button.setEnabled(False)
      self.mic_button.setEnabled(False)
      self.input.setEnabled(False)
      self.voice_core_button.setEnabled(False)

      # -------------------------------------------------
      # CHAT MODE
      # -------------------------------------------------
      # Chat mode shows the acknowledgement as text only.
      # It must NOT speak.
      if self.command_origin == "text":
          self.add_message(
              "HAMMU",
              acknowledgement
          )

          self.start_command_worker(command)
          return

      # -------------------------------------------------
      # VOICE MODE
      # -------------------------------------------------
      if self.command_origin == "voice":
          self.set_voice_state("THINKING")

          self.voice_response.setText(
              acknowledgement
          )

          self.voice_hint.setText(
              "WORKING ON YOUR REQUEST..."
          )

          self.speak_async(
              acknowledgement,
              lambda: self.start_command_worker(command)
          )

    def start_command_worker(self, command):

        self.processing = True

        self.send_button.setEnabled(False)
        self.mic_button.setEnabled(False)
        self.input.setEnabled(False)
        self.voice_core_button.setEnabled(False)

        # The command worker/thread is permanent for the lifetime
        # of HAMMU. Every command is executed on this same thread.
        # This is required because browser.py keeps persistent
        # Playwright objects that must stay on the same thread.
        self.command_worker.command_received.emit(command)

    def command_finished(self, result):
      response = self.normalize_result(result)

      if self.command_origin == "voice":
          self.voice_visualizer_response(response)

          self.speak_async(
              response,
              lambda: QTimer.singleShot(
                700,
                self.start_voice_input
            )   
          )
      else:
          self.add_message(
              "HAMMU",
              response
          )
          self.set_ready_state()

      self.processing = False

      self.send_button.setEnabled(True)
      self.mic_button.setEnabled(True)
      self.input.setEnabled(True)
      self.voice_core_button.setEnabled(True)

      self.input.setFocus()

    def command_error(self, error):

        if self.command_origin == "voice":

            self.visualizer.set_state("RESPONSE")
            self.voice_state.setText("ERROR")

            self.voice_response.setText(
                f"HAMMU error: {error}"
            )

            self.voice_hint.setText(
                "TAP THE CORE TO TRY AGAIN"
            )

        else:

            self.add_message(
                "HAMMU",
                f"I encountered an error: {error}"
            )

            self.set_ready_state()

        self.processing = False

        self.send_button.setEnabled(True)
        self.mic_button.setEnabled(True)
        self.input.setEnabled(True)
        self.voice_core_button.setEnabled(True)

        self.speak_async(
            f"I encountered an error: {error}"
        )

    # -----------------------------------------------------
    # Voice mode
    # -----------------------------------------------------

    def enter_voice_mode(self):

      if self.processing:
          return

      self.header.hide()

      self.pages.setCurrentWidget(
          self.voice_page
      )

      self.voice_transcript.setText(
          "Welcome to HAMMU, your Personal AI Assistant."
      )

      self.voice_response.setText(
          "Audio microphone is activating..."
      )

      self.voice_hint.setText(
          "INITIALIZING VOICE SYSTEM"
      )

      self.set_voice_state(
          "READY"
      )

      self.voice_core_button.setEnabled(False)
      self.back_chat_button.setEnabled(False)

      self.processing = True

      greeting_message = (
          "Welcome to HAMMU, your personal AI assistant. "
          "How can I help you? "
          "Audio microphone is activated."
      )

      self.greeting_thread = QThread()
      self.greeting_worker = GreetingWorker(
          greeting_message
      )

      self.greeting_worker.moveToThread(
          self.greeting_thread
      )

      self.greeting_thread.started.connect(
          self.greeting_worker.run
      )

      self.greeting_worker.finished.connect(
          self.greeting_finished
      )

      self.greeting_worker.error.connect(
          self.greeting_error
      )

      self.greeting_worker.finished.connect(
          self.greeting_thread.quit
      )

      self.greeting_worker.error.connect(
          self.greeting_thread.quit
      )

      self.greeting_thread.finished.connect(
          self.greeting_worker.deleteLater
      )

      self.greeting_thread.finished.connect(
          self.greeting_thread.deleteLater
      )

      self.greeting_thread.start()

    def exit_voice_mode(self):

        if self.processing:
            return

        self.pages.setCurrentWidget(
            self.chat_page
        )

        self.header.show()

        self.set_ready_state()

    def start_voice_input(self):

        if self.processing:
            return

        self.processing = True

        self.voice_core_button.setEnabled(False)
        self.back_chat_button.setEnabled(False)
        self.mic_button.setEnabled(False)
        self.send_button.setEnabled(False)
        self.input.setEnabled(False)

        self.voice_transcript.setText(
            "Listening..."
        )

        self.voice_response.setText("")

        self.set_voice_state(
            "LISTENING"
        )

        self.voice_thread = QThread()
        self.voice_worker = VoiceWorker()

        self.voice_worker.moveToThread(
            self.voice_thread
        )

        self.voice_thread.started.connect(
            self.voice_worker.run
        )

        self.voice_worker.finished.connect(
            self.voice_finished
        )

        self.voice_worker.error.connect(
            self.voice_error
        )

        self.voice_worker.finished.connect(
            self.voice_thread.quit
        )

        self.voice_worker.error.connect(
            self.voice_thread.quit
        )

        self.voice_thread.finished.connect(
            self.voice_worker.deleteLater
        )

        self.voice_thread.finished.connect(
            self.voice_thread.deleteLater
        )

        self.voice_thread.start()

    def voice_finished(self, text):
        
        self.listening_tick_timer.stop()
        text = str(text).strip() if text else ""

        if not text:

            self.voice_transcript.setText(
                "I couldn't understand that."
            )

            self.voice_response.setText(
                "Please try again."
            )

            self.set_voice_state(
                "READY"
            )

            self.voice_core_button.setEnabled(True)
            self.back_chat_button.setEnabled(True)

            self.processing = False

            return

        self.voice_transcript.setText(
            f'YOU SAID: "{text}"'
        )

        self.voice_hint.setText(
            "PROCESSING..."
        )

        self.set_voice_state(
            "THINKING"
        )

        self.command_origin = "voice"

        # Speak an acknowledgement before the command starts.
        self.start_command_worker_with_ack(
            text,
            "Got it. I'm working on that."
        )

    def voice_error(self, error):

        self.listening_tick_timer.stop()
        self.voice_transcript.setText(
            "Microphone error"
        )

        self.voice_response.setText(
            str(error)
        )

        self.voice_hint.setText(
            "TAP THE CORE TO TRY AGAIN"
        )

        self.set_voice_state(
            "READY"
        )

        self.voice_core_button.setEnabled(True)
        self.back_chat_button.setEnabled(True)

        self.processing = False

    # -----------------------------------------------------
    # Voice visual state
    # -----------------------------------------------------

    def set_voice_state(self, state):

        state = state.upper()

        self.voice_state.setText(state)

        self.visualizer.set_state(state)

        if state == "LISTENING":
            self.voice_state.setStyleSheet(
                "color:#63edff;"
                "font-size:15px;"
                "font-weight:700;"
                "letter-spacing:4px;"
            )

        elif state == "THINKING":
            self.voice_state.setStyleSheet(
                "color:#8eb7ff;"
                "font-size:15px;"
                "font-weight:700;"
                "letter-spacing:4px;"
            )

        elif state == "RESPONSE":
            self.voice_state.setStyleSheet(
                "color:#73ffd1;"
                "font-size:15px;"
                "font-weight:700;"
                "letter-spacing:4px;"
            )

        else:
            self.voice_state.setStyleSheet(
                "color:#61e6fa;"
                "font-size:15px;"
                "font-weight:700;"
                "letter-spacing:4px;"
            )

    def voice_visualizer_response(self, response):

        self.set_voice_state(
            "RESPONSE"
        )

        self.voice_response.setText(
            response
        )

        self.voice_hint.setText(
            "TAP THE CORE TO SPEAK AGAIN"
        )

        self.voice_core_button.setEnabled(True)
        self.back_chat_button.setEnabled(True)


    # -----------------------------------------------------
    # General status
    # -----------------------------------------------------

    def set_processing_state(
        self,
        state,
        activity
    ):

        self.status_label.setText(
            f"● {state}"
        )

        self.activity_text.setText(
            activity
        )

    def set_ready_state(self):

        self.status_label.setText(
            "● READY"
        )

        self.activity_text.setText(
            "SYSTEM READY"
        )