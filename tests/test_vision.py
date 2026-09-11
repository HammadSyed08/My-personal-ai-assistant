import ollama

IMAGE_PATH = r"E:\hammu_screenshot.png"

print("==============================================")
print("Hammu AI - Vision Model Test")
print("==============================================")

print("Sending screenshot to Moondream...")

try:
    response = ollama.chat(
        model="moondream:latest",
        messages=[
            {
                "role": "user",
                "content": "Describe everything important you can see in this screenshot. Be concise.",
                "images": [IMAGE_PATH],
            }
        ],
    )

    print("\nVision Response:")
    print(response["message"]["content"])

except Exception as error:
    print("\nVision Error:")
    print(error)