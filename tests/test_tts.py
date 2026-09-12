import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from voice.text_to_speech import text_to_speech


print("Speaking 1...")
text_to_speech.speak("Got it. I'm working on that.")

time.sleep(1)

print("Speaking 2...")
text_to_speech.speak("Hello! I'm Hammu. How can I help you?")

print("Finished.")