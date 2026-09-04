# My-personal-ai-assistant

# ============================================================
# HAMMU AI ASSISTANT - Python Dependencies
# ============================================================

# ------------------------------------------------------------
# PHASE 1 - AI / Ollama
# ------------------------------------------------------------
ollama

# ------------------------------------------------------------
# PHASE 2 - Windows Application Control
# ------------------------------------------------------------
pywin32

# ------------------------------------------------------------
# PHASE 3 - Filesystem / System Utilities
# ------------------------------------------------------------
psutil

# ------------------------------------------------------------
# PHASE 4 + 7 - Browser Automation
# ------------------------------------------------------------
playwright

# ------------------------------------------------------------
# PHASE 5 - Keyboard / Mouse Automation
# ------------------------------------------------------------
pyautogui

# ------------------------------------------------------------
# PHASE 6 - Screen Capture / Computer Vision
# ------------------------------------------------------------
Pillow
opencv-python

# ------------------------------------------------------------
# PHASE 6 - Vision / Image Processing
# ------------------------------------------------------------
numpy

# ------------------------------------------------------------
# PHASE 9 - Voice Input (Speech-to-Text)
# ------------------------------------------------------------
SpeechRecognition
PyAudio

# ------------------------------------------------------------
# PHASE 10 - Voice Output (Text-to-Speech)
# ------------------------------------------------------------
pyttsx3

# ------------------------------------------------------------
# FRONTEND - Professional Desktop GUI
# ------------------------------------------------------------
PySide6

# ------------------------------------------------------------
# Utility / Configuration
# ------------------------------------------------------------
python-dotenv

# ------------------------------------------------------------
# Optional: Better HTTP / API support for future expansion
# ------------------------------------------------------------
requests

# Command Run after Create requirement.txt file
pip install -r requirements.txt

# Then verify the important packages:
python -c "import ollama, playwright, pyautogui, PIL, cv2, numpy, speech_recognition, pyttsx3, PySide6; print('All core packages OK')"


| Component           | Purpose                                 |
| ------------------- | --------------------------------------- |
| `ollama`            | Local AI brain                          |
| `pywin32`           | Windows integration                     |
| `psutil`            | CPU, RAM, processes, system information |
| `playwright`        | Professional browser automation         |
| `pyautogui`         | Keyboard/mouse control                  |
| `Pillow`            | Screenshots/image processing            |
| `opencv-python`     | Computer vision                         |
| `numpy`             | Image/vision calculations               |
| `SpeechRecognition` | Voice → text                            |
| `PyAudio`           | Microphone access                       |
| `pyttsx3`           | Text → voice                            |
| `PySide6`           | Professional Windows GUI                |
| `python-dotenv`     | `.env` configuration                    |
| `requests`          | Future web/API integrations             |



                 ┌──────────────────┐
                 │      HAMMU       │
                 │   AI Assistant   │
                 └────────┬─────────┘
                          │
             ┌────────────┴────────────┐
             │                         │
       Voice Input                 Keyboard
             │                         │
             └────────────┬────────────┘
                          ↓
                 ┌─────────────────┐
                 │ Command Engine  │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │  Ollama / LLM   │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │   Tool Router   │
                 └────────┬────────┘
                          ↓
       ┌──────────┬───────┼───────┬──────────┐
       ↓          ↓       ↓       ↓          ↓
     Apps       Files   Browser  Screen    Keyboard
                                     
                          ↓
                 ┌─────────────────┐
                 │ Voice Response  │
                 └─────────────────┘