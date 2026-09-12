import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from brain.context import context

context.clear_conversation()

context.add_user_message("Who is Elon Musk?")
context.add_assistant_message("Elon Musk is a technology entrepreneur.")

context.add_user_message("How old is he?")

print(context.get_conversation_history())