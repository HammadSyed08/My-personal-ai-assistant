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


## Installation

1. Clone the repo:
   git clone https://github.com/HammadSyed08/My-personal-ai-assistant.git
   cd My-personal-ai-assistant

2. Create a virtual environment:
   python -m venv venv
   venv\Scripts\activate

3. Install Ollama from https://ollama.com, then pull the required models:
   ollama pull llama3.1:8b
   ollama pull moondream

4. Install Python dependencies:
   pip install -r requirements.txt

5. Install Playwright's browser binary:
   python -m playwright install chromium

6. Verify the core packages installed correctly:
   python -c "import ollama, playwright, pyautogui, PIL, cv2, numpy, speech_recognition, pyttsx3, PySide6; print('All core packages OK')"

7. Edit config.py — set CURRENT_WORKING_DIR to a real folder on your machine.
   Edit security/permissions.py — set ALLOWED_DRIVES to match your drives.

8. Run it:
   python main.py


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


# Hammu — Personal AI Assistant

Hammu is a local, Windows-based AI assistant built with **Python** and **[Ollama](https://ollama.com)**. It runs entirely on your own machine: a local LLM (`llama3.1:8b` by default) decides what you want, and a library of Python "tools" carries it out — opening apps, managing files, controlling the browser, moving the mouse, reading the screen, and talking back. No command or file content ever has to leave your laptop.

A full write-up of the architecture, every module, and a step-by-step setup guide is available in **`Hammu_AI_Assistant_Documentation.docx`**. This README is the quick-start version.

## What it can do

- Hold a normal conversation (chat mode)
- Open/close applications (Chrome, Notepad, Calculator, etc.)
- Create, read, rename, move, copy, delete and search files/folders
- Control a real Chrome browser (Google/YouTube search, tabs, back/forward/refresh) via Playwright
- Type text, press keys, move/click the mouse, run hotkeys
- Take screenshots and describe what's on screen using a local vision model (`moondream`)
- Remember facts you tell it ("remember that my favourite editor is VS Code") in a local SQLite database
- Listen to spoken commands and reply out loud (voice mode)
- Run as a full desktop GUI app, not just a terminal

## Architecture at a glance

```
Voice / Keyboard / GUI input
            │
            ▼
core/command_engine.process_command()
   1. Memory command?      ("remember that...")
   2. Context command?     ("open the first result")
   3. Fast local command?  (regex, no AI needed)
   4. Otherwise → ask the AI
            │
            ▼
brain/ollama_brain.ask_ai()  →  local Ollama model  →  JSON decision
   { type: "chat" | "tool" | "plan", ... }
            │
            ▼
execute_tool(tool_name, args)
   security/permissions checks path + confirms dangerous actions
            │
            ▼
   tools/apps.py · files.py · browser.py · input.py · screen.py · vision.py
            │
            ▼
   Printed to console  │  Spoken aloud  │  Shown in GUI
```

Most everyday commands (open/close apps, math, browser tabs, screenshots) are matched instantly by regex in `fast_command()` and never touch the LLM — that's what keeps the assistant responsive on a laptop.

## Project structure

```
main.py               Console entry point (typed + voice mode)
config.py              User-editable settings (model, paths, etc.)
requirements.txt       Python dependencies

brain/                 AI decision-making + conversation context
core/                  Central command router
tools/                 Apps, files, browser, input, screen, vision, calculator
security/              Path allow-list + dangerous-action confirmation
memory/                SQLite-backed long-term memory
voice/                 Speech-to-text / text-to-speech
frontend/              PySide6 desktop GUI
data/                  memory.db (created automatically)
```

## Setup

> This project targets **Windows 10/11** (it uses `pywin32`, Windows-style paths, and Windows TTS voices).

1. **Install Python 3.10–3.12** from [python.org](https://python.org), ticking "Add python.exe to PATH".

2. **Install [Ollama](https://ollama.com)** and pull the two local models this project uses:
   ```
   ollama pull llama3.1:8b
   ollama pull moondream
   ```

3. **Get the project onto your machine** (clone or unzip it) and open a terminal in the project folder.

4. **Create and activate a virtual environment:**
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

5. **Install dependencies:**
   ```
   pip install -r requirements.txt
   python -m playwright install chromium
   ```
   Then verify:
   ```
   python -c "import ollama, playwright, pyautogui, PIL, cv2, numpy, speech_recognition, pyttsx3, PySide6; print('All core packages OK')"
   ```

6. **Configure paths for this machine** — open `config.py` and set `CURRENT_WORKING_DIR` to a real folder/drive that exists on your laptop (it defaults to `E:\`). Update `ALLOWED_DRIVES` / `PROTECTED_DRIVES` in `security/permissions.py` to match. A few tool defaults also hardcode `E:\` screenshot paths (`tools/input.py`, `core/command_engine.py`) — update these too if `E:\` doesn't exist on your system.

7. **Run it:**
   ```
   python main.py            # console mode — type "voice" to switch to voice mode
   ```
   or, for the desktop GUI:
   ```
   cd frontend
   python app.py
   ```

## Configuration reference (`config.py`)

| Setting | Meaning |
|---|---|
| `OLLAMA_MODEL` | Local model used for reasoning/tool selection |
| `OLLAMA_HOST` | Ollama API address |
| `ASSISTANT_NAME` | Name used in replies |
| `CURRENT_WORKING_DIR` | Base folder for resolving relative file paths |
| `VOICE_ENABLED` | Enable/disable voice features |
| `CONFIRM_DANGEROUS_ACTIONS` | Ask yes/no before delete/move actions |

## Security

Every file/folder action is checked against `ALLOWED_DRIVES` / `PROTECTED_DRIVES` in `security/permissions.py` before it runs, and destructive actions (delete, move) require a typed "yes" confirmation. Keep `CURRENT_WORKING_DIR` and `ALLOWED_DRIVES` scoped to a dedicated folder rather than a whole drive until you're confident in how the assistant behaves.

## Dependencies

| Package | Purpose |
|---|---|
| `ollama` | Local AI brain |
| `pywin32` | Windows integration |
| `psutil` | System information |
| `playwright` | Browser automation |
| `pyautogui` | Keyboard/mouse control |
| `Pillow`, `opencv-python`, `numpy` | Screenshots / computer vision |
| `SpeechRecognition`, `sounddevice` | Voice input |
| `pyttsx3` | Voice output |
| `PySide6` | Desktop GUI |
| `python-dotenv` | `.env` configuration |
| `requests` | Future web/API integrations |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| "I encountered an AI processing error" | Ollama not running, or model not pulled | Start Ollama; `ollama pull llama3.1:8b` |
| "ACCESS DENIED" on a file action | Path resolves to a drive not in `ALLOWED_DRIVES` | Update `ALLOWED_DRIVES` / `CURRENT_WORKING_DIR` |
| Screenshot/vision commands fail | Default `E:\` path doesn't exist on this laptop | Update hardcoded default paths |
| Browser commands do nothing | Chrome missing, or Playwright binaries not installed | Install Chrome; `python -m playwright install chromium` |
| Voice mode doesn't hear anything | No mic permission, or no internet (speech recognition is cloud-based) | Grant mic access; check connection |
| GUI won't start | `PySide6` missing, or run from wrong folder | `pip install PySide6`; run `python app.py` from inside `frontend/` |

## Before you push to GitHub

- **Use the provided `.gitignore`.** It excludes `__pycache__/`, your virtual environment, `.env` secrets, your personal memory database (`data/memory.db`), and stray runtime files — while explicitly keeping the `.wav` sound assets under `frontend/assets/` that the GUI needs to run.
- **Double-check `config.py` and `security/permissions.py`** don't contain anything specific to your machine that you don't want public (e.g. real drive letters, personal folder names).
- **Private repo?** A link alone doesn't grant access — you need to add each person as a **Collaborator** (repo → Settings → Collaborators) or make the repo public.
- **Public repo?** Anyone can clone and view the code, but they **cannot push changes** to your repository. Cloning only grants read access. To contribute, someone would need to fork the repo and open a Pull Request, which you'd have to review and merge yourself — or you'd need to explicitly grant them write access as a collaborator.

## Steps for someone cloning this repo

1. Get access (added as a collaborator if private, or the repo is public).
2. `git clone https://github.com/hammadsyed08/my-assistant.git`
3. Follow the **Setup** section above — installing Python, Ollama, dependencies, and editing `config.py` / `security/permissions.py` for their own machine (your `E:\` paths won't exist on theirs).

For the full architecture explanation, a component-by-component walkthrough, and how to add new tools, see **`Hammu_AI_Assistant_Documentation.docx`**.