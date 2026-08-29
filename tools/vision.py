import os
import re
import ollama
import pyautogui


VISION_MODEL = "moondream:latest"

DEFAULT_SCREENSHOT = r"E:\hammu_screenshot.png"


def locate_element_coordinates(target: str, image_path: str = r"E:\hammu_screen.png"):
    """
    Asks Moondream for the location of an object and converts 
    normalized ratios into actual pixel coordinates (X, Y).
    """
    # 1. Get real monitor dimensions
    screen_width, screen_height = pyautogui.size()

    # 2. Prompt Moondream to output normalized coordinates (0.0 to 1.0)
    prompt = (
        f"Detect the target element: '{target}'. "
        f"Respond ONLY with coordinates in format: x: 0.XX, y: 0.YY"
    )

    try:
        response = ollama.chat(
            model="moondream:latest",
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [image_path]
            }]
        )

        answer = response.get("message", {}).get("content", "")

        # 3. Extract x and y floats from model response using regex
        match = re.search(r"x:\s*([0-9.]+),\s*y:\s*([0-9.]+)", answer, re.IGNORECASE)

        if match:
            norm_x = float(match.group(1))
            norm_y = float(match.group(2))

            # Convert 0.0-1.0 ratio into display pixels
            pixel_x = int(norm_x * screen_width)
            pixel_y = int(norm_y * screen_height)

            return {
                "success": True,
                "x": pixel_x,
                "y": pixel_y
            }

        # Fallback if specific format missing: try matching any two decimals
        numbers = re.findall(r"0\.\d+", answer)
        if len(numbers) >= 2:
            pixel_x = int(float(numbers[0]) * screen_width)
            pixel_y = int(float(numbers[1]) * screen_height)
            return {"success": True, "x": pixel_x, "y": pixel_y}

        return {
            "success": False,
            "error": f"Could not parse coordinates from vision output: '{answer}'"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

def analyze_screen(
    image_path=DEFAULT_SCREENSHOT,
    question="Describe what is currently visible on the screen."
):
    """
    Analyze a screenshot using the local Moondream vision model.
    """

    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": f"Screenshot not found: {image_path}"
        }

    try:
        print("[Vision] Sending screenshot to Moondream...")

        vision_prompt = f"""
Analyze this screenshot carefully.

Task:
{question}

Instructions:
- Look carefully at the entire screenshot.
- Identify the relevant application, website, text, error, or UI element if visible.
- Answer the task directly.
- Base your answer only on what is visible in the screenshot.
- If the requested information is not visible, clearly say that.
- Always provide a concise non-empty answer.
"""

        response = ollama.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": vision_prompt,
                    "images": [image_path],
                }
            ],
        )

        answer = response.get("message", {}).get("content", "").strip()

        print("[Vision] Response:")
        print(repr(answer))

        if not answer:
            return {
                "success": False,
                "error": "Moondream returned an empty response."
            }

        return {
            "success": True,
            "answer": answer
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }