import time
import pyautogui


# ============================================================
# SAFETY
# ============================================================

# PyAutoGUI will immediately stop if the mouse is moved
# to the top-left corner of the screen.
pyautogui.FAILSAFE = True

# Small delay between PyAutoGUI actions.
pyautogui.PAUSE = 0.15


# ============================================================
# TYPE TEXT
# ============================================================

def type_text(text):

    if not text:

        return "No text was provided."

    try:

        pyautogui.write(
            text,
            interval=0.03
        )

        return f"Typed: {text}"

    except Exception as error:

        return f"Typing failed: {error}"


# ============================================================
# PRESS KEY
# ============================================================

def press_key(key):

    if not key:

        return "No key was provided."

    key = key.lower().strip()

    try:

        pyautogui.press(key)

        return f"Pressed key: {key}"

    except Exception as error:

        return f"Key press failed: {error}"


# ============================================================
# HOTKEY
# ============================================================

def hotkey(keys):

    if not keys:

        return "No keyboard combination was provided."

    try:

        if isinstance(keys, str):

            keys = keys.replace(
                "+",
                " "
            ).split()

        pyautogui.hotkey(*keys)

        return (
            "Pressed hotkey: "
            + " + ".join(keys)
        )

    except Exception as error:

        return f"Hotkey failed: {error}"


# ============================================================
# WRITE TEXT WITH INTERVAL
# ============================================================

def write_text(text, interval=0.03):

    if not text:

        return "No text was provided."

    try:

        pyautogui.write(
            text,
            interval=interval
        )

        return f"Successfully typed: {text}"

    except Exception as error:

        return f"Typing failed: {error}"
# ============================================================
# MOVE MOUSE
# ============================================================

def move_mouse(x, y, duration=0.3):

    try:

        x = int(x)
        y = int(y)

        pyautogui.moveTo(
            x,
            y,
            duration=duration
        )

        return f"Mouse moved to ({x}, {y})."

    except Exception as error:

        return f"Mouse movement failed: {error}"


# ============================================================
# CLICK
# ============================================================

def click_mouse(
    button="left",
    clicks=1
):

    try:

        pyautogui.click(
            button=button,
            clicks=int(clicks)
        )

        return (
            f"Mouse clicked "
            f"{button} button."
        )

    except Exception as error:

        return f"Mouse click failed: {error}"


# ============================================================
# DOUBLE CLICK
# ============================================================

def double_click():

    try:

        pyautogui.doubleClick()

        return "Double-clicked."

    except Exception as error:

        return f"Double-click failed: {error}"


# ============================================================
# RIGHT CLICK
# ============================================================

def right_click():

    try:

        pyautogui.rightClick()

        return "Right-clicked."

    except Exception as error:

        return f"Right-click failed: {error}"


# ============================================================
# SCROLL
# ============================================================

def scroll_mouse(amount):

    try:

        amount = int(amount)

        pyautogui.scroll(amount)

        return f"Scrolled {amount}."

    except Exception as error:

        return f"Scrolling failed: {error}"
# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot(path="E:\\hammu_screenshot.png"):

    try:

        screenshot = pyautogui.screenshot()

        screenshot.save(path)

        return (
            f"Screenshot saved successfully: "
            f"{path}"
        )

    except Exception as error:

        return f"Screenshot failed: {error}"