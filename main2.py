import os
import subprocess
import time
import speech_recognition as sr
import pyautogui
import ollama
import sounddevice as sd
import webbrowser  # Natively opens web browsers and searches URLs

# Track the last active path used by the agent to handle context (like renaming a folder you just made)
CURRENT_WORKING_DIR = "D:\\"

def execute_system_action(action_type, details, original_phrase=""):
    global CURRENT_WORKING_DIR
    details_clean = details.lower().strip()
    
    # ==================== OPEN COMMANDS ====================
    if action_type == "open":
        print(f"[Agent] Opening -> {details_clean}")
        
        if "notepad" in details_clean:
            subprocess.Popen(["notepad.exe"])
        elif "calculator" in details_clean or "calc" in details_clean:
            subprocess.Popen(["calc.exe"])
        elif "chrome" in details_clean or "browser" in details_clean:
            # Opens your default web browser (usually Chrome) directly to Google
            webbrowser.open("https://google.com")
            
        # --- SYSTEM NAVIGATION ---
        elif "this pc" in details_clean or "my computer" in details_clean:
            subprocess.Popen(["explorer.exe", "::{20D04FE0-3AEA-1069-A2D8-08002B30309D}"])
        elif "c drive" in details_clean:
            CURRENT_WORKING_DIR = "C:\\"
            os.system("start C:")
        elif "d drive" in details_clean:
            CURRENT_WORKING_DIR = "D:\\"
            os.system("start D:")
            
        # --- TARGET FOLDERS ---
        elif "folder" in details_clean:
            if "download" in details_clean:
                CURRENT_WORKING_DIR = os.path.expanduser("~/Downloads")
                os.startfile(CURRENT_WORKING_DIR)
            elif "desktop" in details_clean:
                CURRENT_WORKING_DIR = os.path.expanduser("~/Desktop")
                os.startfile(CURRENT_WORKING_DIR)
            else:
                folder_name = details_clean.replace("named", "").replace("folder", "").strip()
                target_path = f"D:\\{folder_name}"
                learning_path = f"D:\\My Learning\\Python\\{folder_name}"
                
                if os.path.exists(target_path):
                    CURRENT_WORKING_DIR = target_path
                    os.startfile(target_path)
                elif os.path.exists(learning_path):
                    CURRENT_WORKING_DIR = learning_path
                    os.startfile(learning_path)
                else:
                    print(f"[Agent] Error: Could not find folder '{folder_name}'")

    # ==================== WEB SEARCH COMMANDS ====================
    elif action_type == "search":
        print(f"[Agent] Searching -> {details}")
        if "youtube" in original_phrase.lower():
            # Formats search string into a YouTube search query URL
            search_url = f"https://youtube.com{details.replace(' ', '+')}"
            webbrowser.open(search_url)
        else:
            # Performs a standard Google Search
            search_url = f"https://google.com/search?q={details.replace(' ', '+')}"
            webbrowser.open(search_url)

    # ==================== FILE MANAGEMENT SYSTEM ====================
    elif action_type == "create_folder":
        # Combines your current working drive with the name you spoke
        new_folder_path = os.path.join(CURRENT_WORKING_DIR, details)
        try:
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
                print(f"[Agent] Successfully created folder: {new_folder_path}")
                os.startfile(CURRENT_WORKING_DIR)  # Pops open the window to show you the folder
            else:
                print("[Agent] That folder already exists.")
        except Exception as e:
            print(f"[Agent] Failed to create folder. Error: {e}")

    elif action_type == "rename_folder":
        # Expected phrase format: "rename folder oldname to newname"
        if " to " in details_clean:
            parts = details.split(" to ")
            old_name = parts[0].strip()
            new_name = parts[1].strip()
            
            old_path = os.path.join(CURRENT_WORKING_DIR, old_name)
            new_path = os.path.join(CURRENT_WORKING_DIR, new_name)
            
            try:
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    print(f"[Agent] Renamed '{old_name}' to '{new_name}' successfully.")
                else:
                    print(f"[Agent] Error: Could not find a folder named '{old_name}' in {CURRENT_WORKING_DIR}")
            except Exception as e:
                print(f"[Agent] Rename operation failed: {e}")
        else:
            print("[Agent] Incorrect format. Say: 'rename folder [old name] to [new name]'")

    # ==================== CLOSE & AUTOMATION COMMANDS ====================
    elif action_type == "close":
        print(f"[Agent] Closing -> {details_clean}")
        if "notepad" in details_clean:
            os.system("taskkill /f /im notepad.exe")
        elif "calculator" in details_clean or "calc" in details_clean:
            os.system("taskkill /f /im CalculatorApp.exe")
            os.system("taskkill /f /im calc.exe")
        elif "chrome" in details_clean or "browser" in details_clean:
            os.system("taskkill /f /im chrome.exe")
        elif "folder" in details_clean or "explorer" in details_clean:
            os.system("taskkill /f /im explorer.exe & start explorer.exe")
            
    elif action_type == "type":
        print(f"[Agent] Automating typing...")
        time.sleep(1.5)  
        pyautogui.write(details, interval=0.02)

# Microphone Stream Reader
def capture_audio_input():
    recognizer = sr.Recognizer()
    print("\n[Listening...] Speak agent command...")
    try:
        duration = 5
        sample_rate = 16000
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        audio_data = sr.AudioData(recording.tobytes(), sample_rate, 2)
        parsed_text = recognizer.recognize_google(audio_data)
        print(f"[Agent Heard]: {parsed_text}")
        return parsed_text
    except Exception:
        return None

# Agent Main Decision Loop
def run_voice_assistant():
    print("==================================================================")
    print("PRO AI AGENT ONLINE. Web Browsing & File Management Unlocked.")
    print("==================================================================")
    
    while True:
        voice_command = capture_audio_input()
        if not voice_command:
            continue
            
        cmd_lower = voice_command.lower()
        
        if "exit" in cmd_lower or "stop" in cmd_lower:
            print("[Agent] Shutting down agent architecture. Goodbye!")
            break
            
        # 1. CLOSE RULE
        if "close" in cmd_lower or "shutdown" in cmd_lower:
            execute_system_action("close", cmd_lower.replace("close", "").strip())
                
        # 2. CREATE FOLDER RULE ("create folder named test")
        elif "create folder" in cmd_lower:
            folder_name = cmd_lower.split("folder", 1)[1].replace("named", "").strip()
            execute_system_action("create_folder", folder_name)
            
        # 3. RENAME FOLDER RULE ("rename folder old to new")
        elif "rename folder" in cmd_lower:
            rename_details = cmd_lower.split("folder", 1)[1].strip()
            execute_system_action("rename_folder", rename_details)

        # 4. YOUTUBE SEARCH RULE ("search youtube for standard data")
        elif "search youtube for" in cmd_lower:
            search_query = voice_command.lower().split("youtube for", 1)[1].strip()
            execute_system_action("search", search_query, original_phrase=voice_command)

        # 5. GOOGLE SEARCH RULE ("search google for standard data")
        elif "search google for" in cmd_lower or "search for" in cmd_lower:
            split_word = "google for" if "google for" in cmd_lower else "search for"
            search_query = voice_command.lower().split(split_word, 1)[1].strip()
            execute_system_action("search", search_query, original_phrase=voice_command)

        # 6. OPEN RULE
        elif "open" in cmd_lower:
            app_details = voice_command.split("open", 1)[1].strip()
            execute_system_action("open", app_details)
            
        # 7. TYPE RULE
        elif "type" in cmd_lower or "write" in cmd_lower:
            trigger_word = "type" if "type" in cmd_lower else "write"
            try:
                text_payload = voice_command.split(trigger_word, 1)[1].strip()
                execute_system_action("type", text_payload)
            except IndexError:
                pass
                
        # 8. GENERAL AI KNOWLEDGE FALLBACK
        else:
            try:
                system_prompt = "You are a professional desktop AI voice assistant. Give extremely precise, short responses under two sentences."
                ai_query = ollama.chat(model='llama3.1:8b', messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': voice_command}
                ])
                print(f"[AI Agent Brain]: {ai_query['message']['content']}")
            except Exception as system_error:
                print(f"[Ollama Error] Agent brain disconnected. Details: {system_error}")

if __name__ == "__main__":
    run_voice_assistant()
