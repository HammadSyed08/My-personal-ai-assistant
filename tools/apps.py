import subprocess
import os


APPLICATIONS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",

    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",

    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
}


def open_application(name):

    name = name.lower().strip()

    # Direct application mapping
    if name in APPLICATIONS:

        command = APPLICATIONS[name]

        try:

            subprocess.Popen(command)

            return f"{name} opened successfully."

        except FileNotFoundError:

            return (
                f"I couldn't find {name} at the expected location."
            )

        except Exception as error:

            return f"Could not open {name}: {error}"

    # Try Windows Start command
    try:

        subprocess.Popen(
            f'start "" "{name}"',
            shell=True
        )

        return f"I tried to open {name}."

    except Exception as error:

        return f"Could not open {name}: {error}"


def close_application(name):

    name = name.lower().strip()

    processes = {
        "notepad": "notepad.exe",
        "calculator": "CalculatorApp.exe",
        "calc": "CalculatorApp.exe",
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "paint": "mspaint.exe",
    }

    process = processes.get(name)

    if not process:

        return (
            f"I don't know the Windows process for {name}."
        )

    try:

        result = subprocess.run(
            [
                "taskkill",
                "/F",
                "/IM",
                process
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:

            return f"{name} closed successfully."

        return f"{name} was not running."

    except Exception as error:

        return f"Could not close {name}: {error}"