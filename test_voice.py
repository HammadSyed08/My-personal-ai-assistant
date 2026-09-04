from voice.speech_to_text import speech_to_text


print("=" * 50)
print("HAMMU VOICE INPUT TEST")
print("=" * 50)

text = speech_to_text.listen()

print("\nResult:")

if text:
    print(text)
else:
    print("No text received.")