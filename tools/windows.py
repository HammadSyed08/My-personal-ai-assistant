import ctypes
import re


user32 = ctypes.windll.user32


def get_active_window():
    """
    Get information about the currently active Windows window.
    """

    hwnd = user32.GetForegroundWindow()

    if not hwnd:
        return {
            "success": False,
            "error": "Could not determine the active window."
        }

    length = user32.GetWindowTextLengthW(hwnd)

    if length == 0:
        return {
            "success": True,
            "title": "Unknown",
            "application": "Unknown"
        }

    buffer = ctypes.create_unicode_buffer(length + 1)

    user32.GetWindowTextW(
        hwnd,
        buffer,
        length + 1
    )

    title = buffer.value.strip()

    # Common Windows title pattern:
    # "filename - folder - Visual Studio Code"
    application = "Unknown"

    if " - Visual Studio Code" in title:
        application = "Visual Studio Code"

    elif " - Google Chrome" in title:
        application = "Google Chrome"

    elif " - Mozilla Firefox" in title:
        application = "Mozilla Firefox"

    elif " - Microsoft Edge" in title:
        application = "Microsoft Edge"

    elif " - Notepad" in title:
        application = "Notepad"

    elif title.endswith("Calculator"):
        application = "Calculator"

    return {
        "success": True,
        "title": title,
        "application": application
    }

def get_work_context():
    """
    Get the current application and extract basic work context
    from the active window title.
    """

    result = get_active_window()

    if not result.get("success"):
        return result

    application = result.get(
        "application",
        "Unknown application"
    )

    title = result.get(
        "title",
        "Unknown window"
    )

    file_name = None
    project_name = None

    if application == "Visual Studio Code":
        parts = [
            part.strip()
            for part in title.split(" - ")
        ]

        if len(parts) >= 2:
            file_name = parts[0]
            project_name = parts[1]

    return {
        "success": True,
        "application": application,
        "title": title,
        "file": file_name or "Unknown",
        "project": project_name or "Unknown"
    }