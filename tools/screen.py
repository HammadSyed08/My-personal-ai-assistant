import os
import pyautogui


# ============================================================
# SCREEN INFORMATION
# ============================================================

def get_screen_size():

    try:

        width, height = pyautogui.size()

        return {
            "width": width,
            "height": height
        }

    except Exception as error:

        return {
            "error": str(error)
        }


# ============================================================
# TAKE SCREENSHOT
# ============================================================

def take_screen_screenshot(
    path="E:\\hammu_screen.png"
):

    try:

        # Make sure the directory exists
        directory = os.path.dirname(path)

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        screenshot = pyautogui.screenshot()

        screenshot.save(path)

        return {
            "success": True,
            "path": path,
            "width": screenshot.width,
            "height": screenshot.height
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }

if __name__ == "__main__":

    print("Screen size:")

    print(
        get_screen_size()
    )

    print(
        "\nTaking screenshot..."
    )

    result = take_screen_screenshot()

    print(result)