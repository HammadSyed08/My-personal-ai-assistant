import json
import re
import ollama

from config import OLLAMA_MODEL


# ============================================================
# SMALL + FAST AI PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Hammu, a Windows desktop assistant.

Return ONLY valid JSON.

You have two response types.

CHAT:
{
  "type": "chat",
  "response": "short response"
}

TOOL:
{
  "type": "tool",
  "tool": "TOOL_NAME",
  "args": {}
}

PLAN:
{
  "type": "plan",
  "steps": [
    {
      "tool": "TOOL_NAME",
      "args": {}
    }
  ]
}

Available tools:

open_application:
{"name":"chrome"}

close_application:
{"name":"chrome"}

create_folder:
{"path":"Projects"}

open_folder:
{"path":"Projects"}

list_directory:
{"path":"Projects"}

create_file:
{"path":"Projects/hello.txt","content":"Hello"}

read_file:
{"path":"Projects/hello.txt"}

rename_item:
{"old_path":"Projects/hello.txt","new_name":"welcome.txt"}

copy_item:
{"source":"Projects/hello.txt","destination":"Backup"}

move_item:
{"source":"Projects/hello.txt","destination":"Documents"}

delete_file:
{"path":"Projects/hello.txt"}

delete_folder:
{"path":"Projects"}

get_current_directory:
{}

search_files:
{"search_term":"invoice","location":"E:\\"}

open_url:
{"url":"https://github.com"}

google_search:
{"query":"Python tutorial"}

youtube_search:
{"query":"n8n tutorial"}

type_text:
{"text":"Hello Hammad"}

press_key:
{"key":"enter"}

hotkey:
{"keys":["ctrl","c"]}

move_mouse:
{"x":500,"y":300}

click_mouse:
{"button":"left","clicks":1}

double_click:
{}

right_click:
{}

scroll_mouse:
{"amount":5}

take_screenshot:
{"path":"E:\\hammu_screenshot.png"}

take_screen_screenshot:
{"path":"E:\\hammu_screen.png"}

analyze_screen:
{"question":"What is currently visible on the screen?","path":"E:\\hammu_screen.png"}

locate_and_click:
{"target": "Chrome icon"}

get_screen_size:
{}

Rules:

1. Use tools for computer actions.
2. Never invent tools.
3. Never invent arguments.
4. "close" means close_application.
5. "open", "launch", "start" means open_application.
6. "write" or "type" means type_text when the user wants keyboard input.
7. "what is inside", "what's inside", "list", or "show files" means list_directory.
8. Screenshot requests use take_screenshot.
9. Questions about what is visible on the screen use analyze_screen.
10. Never invent a tool that is not listed.
11. Use relative paths when possible.
12. Keep chat responses short.
13. For multiple actions, return a plan.
"""


# ============================================================
# FAST LOCAL COMMAND DETECTION
# ============================================================

def fast_command(user_message):
    """
    Handle very common commands without calling Ollama.

    This is the most important performance optimization.
    """

    text = user_message.strip()
    lower = text.lower()

    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    if re.search(r"\b(take|capture|get)\b.*\b(screenshot|screen shot)\b", lower):
        return {
            "type": "tool",
            "tool": "take_screenshot",
            "args": {
                "path": r"E:\hammu_screenshot.png"
            }
        }
# --------------------------------------------------------
# ACTIVE WINDOW / APPLICATION
# --------------------------------------------------------

    active_window_patterns = [
        r"\bwhich app is open\b",
        r"\bwhat app is open\b",
        r"\bwhich application is open\b",
        r"\bwhat application is open\b",
        r"\bwhich program is open\b",
        r"\bwhat program is open\b",
        r"\bwhich app am i using\b",
        r"\bwhat app am i using\b",
        r"\bwhich application am i using\b",
        r"\bwhat application am i using\b",
        r"\bwhat window is active\b",
        r"\bwhich window is active\b",
        r"\bwhat is the active window\b",
        r"\bwhich window is currently active\b",
        r"\bwhat is the current active window\b",
        r"\bwhich window is currently open\b",
        r"\bwhat is the current open window\b",
        r"\bwhich window is open\b",
        r"\bwhat is the open window\b",
        r"\bwhich window is active\b",
        r"\bwhat is the active window\b",
    ]

    if any(re.search(pattern, lower) for pattern in active_window_patterns):
        return {
            "type": "tool",
            "tool": "get_active_window",
            "args": {}
        }

    # --------------------------------------------------------
    # WORK CONTEXT
    # --------------------------------------------------------

    work_context_patterns = [
        r"\bwhat am i working on\b",
        r"\bwhat am i currently working on\b",
        r"\bwhat am i working on right now\b",
        r"\bwhat file am i working on\b",
        r"\bwhat file am i editing\b",
        r"\bwhich file am i editing\b",
        r"\bwhat project am i working on\b",
        r"\bwhich project am i working on\b",
    ]

    if any(
        re.search(pattern, lower)
        for pattern in work_context_patterns
    ):
        return {
            "type": "tool",
            "tool": "get_work_context",
            "args": {}
        }

    # --------------------------------------------------------
# SCREEN ANALYSIS / VISION
# --------------------------------------------------------
    screen_analysis_patterns = [
        r"\bwhat('?s| is) on my screen\b",
        r"\bwhat('?s| is) on the screen\b",
        r"\bwhat am i looking at\b",
        r"\bwhat do you see on my screen\b",
        r"\bwhat can you see on my screen\b",
        r"\blook at my screen\b",
        r"\banalyze my screen\b",
        r"\banalyse my screen\b",
        r"\bdescribe my screen\b",
        r"\bdescribe what('?s| is) on my screen\b",
        r"\btell me what('?s| is) on my screen\b",
        r"\bwhich app(lication)? is open\b",
        r"\bwhat app(lication)? is open\b",
        r"\bwhat app(lication)? am i using\b",
        r"\bwhich program is open\b",
        r"\bwhat program is open\b",
        r"\bwhat error is (showing|visible|displayed)\b",
        r"\bwhat error.*screen\b",
        r"\bwhat is showing on my screen\b",
        r"\bwhat is visible on my screen\b",
        r"\bread.*screen\b",
        r"\bwhat website is open\b",
        r"\bwhich website is open\b",
        r"\bwhat site is open\b",
        r"\bwhich site is open\b",
        r"\bwhat website.*screen\b",
        r"\bwhich website.*screen\b",
        r"\bwhat site.*screen\b",
        r"\bwhich site.*screen\b",
    ]

    if any(
        re.search(pattern, lower)
        for pattern in screen_analysis_patterns
    ):
        return {
            "type": "tool",
            "tool": "analyze_screen",
            "args": {
                "question": user_message,
                "path": r"E:\hammu_screen.png"
            }
        }

        # --------------------------------------------------------
        # SCREEN SIZE
        # --------------------------------------------------------

        if "screen size" in lower or "resolution" in lower:
            return {
                "type": "tool",
                "tool": "get_screen_size",
                "args": {}
            }
# --------------------------------------------------------
# OPEN CHROME PROFILE
# --------------------------------------------------------

    chrome_profile_patterns = [
        r"^open\s+(.+?)\s+profile$",
        r"^open\s+(.+?)\s+profile\s+in\s+chrome$",
        r"^open\s+(.+?)\s+chrome\s+profile$",
        r"^open\s+chrome\s+profile\s+(.+)$",
        r"^switch\s+to\s+(.+?)\s+profile$",
        r"^switch\s+to\s+(.+?)\s+profile\s+in\s+chrome$",
    ]

    for pattern in chrome_profile_patterns:

        profile_match = re.match(
            pattern,
            text.strip(),
            re.IGNORECASE
        )

        if profile_match:

            profile_name = profile_match.group(1).strip()

            return {
                "type": "tool",
                "tool": "open_chrome_profile",
                "args": {
                    "profile_name": profile_name
                }
            }

# ========================================================
# OPEN WEBSITE
# ========================================================

    website_match = re.match(
        r"^(open|launch|start|go to)\s+(?:the\s+)?(.+?)\s*(?:website|site)?$",
        lower
    )

    if website_match:
        target = website_match.group(2).strip()

        websites = {
            "google": "google",
            "youtube": "youtube",
            "github": "github",
            "chatgpt": "chatgpt",
            "gmail": "gmail",
            "facebook": "facebook",
            "linkedin": "linkedin",
            "whatsapp": "whatsapp",
            "stackoverflow": "stackoverflow",
            "reddit": "reddit",
        }

        if target in websites:
            return {
                "type": "tool",
                "tool": "open_website",
                "args": {
                    "name": websites[target]
                }
            }

        # --------------------------------------------------------
        # OPEN APPLICATION
        # --------------------------------------------------------

        open_match = re.match(
            r"^(open|launch|start|run)\s+(.+)$",
            lower
        )

        if open_match:

            target = open_match.group(2).strip()

            # Remove common polite words
            target = re.sub(
                r"^(the|my)\s+",
                "",
                target
            )

            applications = {
                "chrome": "chrome",
                "google chrome": "chrome",
                "notepad": "notepad",
                "calculator": "calculator",
                "calc": "calculator",
            }

            if target in applications:
                return {
                    "type": "tool",
                    "tool": "open_application",
                    "args": {
                        "name": applications[target]
                    }
                }

        # --------------------------------------------------------
        # CLOSE APPLICATION
        # --------------------------------------------------------

        close_match = re.match(
            r"^(close|exit|quit|terminate|shut)\s+(.+)$",
            lower
        )

        if close_match:

            target = close_match.group(2).strip()

            target = re.sub(
                r"^(the|my)\s+",
                "",
                target
            )

            applications = {
                "chrome": "chrome",
                "google chrome": "chrome",
                "notepad": "notepad",
                "calculator": "calculator",
                "calc": "calculator",
            }

            if target in applications:
                return {
                    "type": "tool",
                    "tool": "close_application",
                    "args": {
                        "name": applications[target]
                    }
                }

        # --------------------------------------------------------
        # PRESS KEY
        # --------------------------------------------------------

        key_match = re.match(
            r"^press\s+(.+)$",
            lower
        )

        if key_match:

            key = key_match.group(1).strip()

            key_map = {
                "enter": "enter",
                "return": "enter",
                "tab": "tab",
                "escape": "esc",
                "esc": "esc",
                "backspace": "backspace",
                "delete": "delete",
                "space": "space",
                "home": "home",
                "end": "end",
                "up": "up",
                "down": "down",
                "left": "left",
                "right": "right",
                "f5": "f5",
            }

            if key in key_map:
                return {
                    "type": "tool",
                    "tool": "press_key",
                    "args": {
                        "key": key_map[key]
                    }
                }

        # --------------------------------------------------------
        # TYPE / WRITE
        # --------------------------------------------------------

        type_match = re.match(
            r"^(type|write)\s+(.+)$",
            text,
            re.IGNORECASE
        )

        if type_match:

            typed_text = type_match.group(2).strip()

            return {
                "type": "tool",
                "tool": "type_text",
                "args": {
                    "text": typed_text
                }
            }

        # --------------------------------------------------------
        # OPEN SPECIAL WINDOWS FOLDERS
        # --------------------------------------------------------

        folder_match = re.match(
            r"^(open|show)\s+(my\s+)?(downloads|documents|desktop|pictures|videos|music)(\s+folder)?$",
            lower
        )

        if folder_match:

            folder = folder_match.group(3)

            return {
                "type": "tool",
                "tool": "open_folder",
                "args": {
                    "path": folder.capitalize()
                }
            }

        # --------------------------------------------------------
        # LIST DIRECTORY
        # --------------------------------------------------------

        inside_match = re.match(
            r"^(what('s| is) inside|what('s| is) in|list|show)\s+(the\s+)?(.+?)(\s+folder)?$",
            lower
        )

        if inside_match:

            folder = inside_match.group(5).strip()

            if folder:
                return {
                    "type": "tool",
                    "tool": "list_directory",
                    "args": {
                        "path": folder
                    }
                }

        # --------------------------------------------------------
        # CREATE FOLDER
        # --------------------------------------------------------

        create_match = re.match(
            r"^create\s+(a\s+)?folder\s+(called|named)\s+(.+)$",
            lower
        )

        if create_match:

            folder_name = create_match.group(3).strip()

            return {
                "type": "tool",
                "tool": "create_folder",
                "args": {
                    "path": folder_name
                }
            }

        return None
    # Locate & Click regex pattern
    click_match = re.match(r"^(click|press|select)\s+(on\s+)?(the\s+)?(.+?)$", lower)
    if click_match and not any(k in lower for k in ["button", "key", "mouse"]):
        target_item = click_match.group(4).strip()
        return {
            "type": "tool",
            "tool": "locate_and_click",
            "args": {
                "target": target_item
            }
        }


# ========================================================
# YOUTUBE SEARCH
# ========================================================

    youtube_match = re.match(
        r"^(?:search|find)\s+(?:on\s+)?youtube\s+(?:for\s+)?(.+)$",
        text,
        re.IGNORECASE
    )

    if youtube_match:
        query = youtube_match.group(1).strip()

        if query:
            return {
                "type": "tool",
                "tool": "youtube_search",
                "args": {
                    "query": query
                }
            }


# ========================================================
# GOOGLE SEARCH
# ========================================================

    google_match = re.match(
        r"^(?:search|find)\s+(?:on\s+)?google\s+(?:for\s+)?(.+)$",
        text,
        re.IGNORECASE
    )

    if google_match:
        query = google_match.group(1).strip()

        if query:
            return {
                "type": "tool",
                "tool": "google_search",
                "args": {
                    "query": query
                }
            }

# --------------------------------------------------------
# BROWSER NEW TAB
# --------------------------------------------------------

        if re.search(
            r"^\s*(open|create|new)\s+(a\s+)?new\s+tab\s*$",
            lower
        ):
            return {
                "type": "tool",
                "tool": "browser_new_tab",
                "args": {}
            }

# --------------------------------------------------------
# BROWSER CLOSE TAB
# --------------------------------------------------------

        if re.search(
            r"^\s*(close|exit)\s+(this\s+)?tab\s*$",
            lower
        ):
            return {
                "type": "tool",
                "tool": "browser_close_tab",
                "args": {}
            }

# --------------------------------------------------------
# BROWSER NEXT TAB
# --------------------------------------------------------

        if re.search(
            r"^\s*(next|switch to next)\s+tab\s*$",
            lower
        ):
            return {
                "type": "tool",
                "tool": "browser_next_tab",
                "args": {}
            }

# --------------------------------------------------------
# BROWSER PREVIOUS TAB
# --------------------------------------------------------

        if re.search(
            r"^\s*(previous|last|switch to previous)\s+tab\s*$",
            lower
        ):
            return {
                "type": "tool",
                "tool": "browser_previous_tab",
                "args": {}
            }

# --------------------------------------------------------
# BROWSER LIST TABS
# --------------------------------------------------------

        if re.search(
            r"^\s*(list|show)\s+(all\s+)?tabs\s*$",
            lower
        ):
            return {
                "type": "tool",
                "tool": "browser_list_tabs",
                "args": {}
            }
    
# --------------------------------------------------------
# BROWSER BACK
# --------------------------------------------------------

    if re.search(
        r"^(go back|back|browser back)$",
        lower
    ):
        return {
            "type": "tool",
            "tool": "browser_back",
            "args": {}
        }

# --------------------------------------------------------
# BROWSER FORWARD
# --------------------------------------------------------

    if re.search(
        r"^(go forward|forward|browser forward)$",
        lower
    ):
        return {
            "type": "tool",
            "tool": "browser_forward",
            "args": {}
        }

# --------------------------------------------------------
# BROWSER REFRESH
# --------------------------------------------------------

    if re.search(
        r"^(refresh|refresh page|reload|reload page)$",
        lower
    ):
        return {
            "type": "tool",
            "tool": "browser_refresh",
            "args": {}
        }

# --------------------------------------------------------
# BROWSER PAGE TITLE
# --------------------------------------------------------

    if re.search(
        r"^(what page is open|which page is open|what page is this|what website is open|which website is open|what site is open|which site is open)$",
        lower
    ):
        return {
            "type": "tool",
            "tool": "get_page_title",
            "args": {}
        }


# --------------------------------------------------------
# CURRENT URL
# --------------------------------------------------------

    if re.search(
        r"^(what is the current url|what's the current url|show current url|what url is open|which url is open)$",
        lower
    ):
        return {
            "type": "tool",
            "tool": "get_current_url",
            "args": {}
        }


# --------------------------------------------------------
# CLOSE BROWSER
# --------------------------------------------------------

    if re.search(
        r"^(close browser|exit browser|quit browser)$",
        lower
    ):
        return {
            "type": "tool",
            "tool": "close_browser",
            "args": {}
        }

# --------------------------------------------------------
# FIND BROWSER ELEMENT
# --------------------------------------------------------

    find_element_patterns = [
        r"^find\s+(?:the\s+)?(.+)$",
        r"^locate\s+(?:the\s+)?(.+)$",
        r"^find\s+(?:the\s+)?(.+?)\s+(?:element|field|box|button)$",
    ]

    for pattern in find_element_patterns:

        match = re.match(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            target = match.group(1).strip()

            return {
                "type": "tool",
                "tool": "find_element",
                "args": {
                    "target": target
                }
            }

    return None


# ============================================================
# OLLAMA FALLBACK
# ============================================================

def ask_ai(user_message):
    """
    Main AI router.

    Fast commands are handled locally without Ollama.
    Only commands that require AI reasoning are sent to Ollama.
    """

    # ============================================================
    # FAST LOCAL COMMAND ROUTER
    # ============================================================

    fast_result = fast_command(user_message)

    if fast_result is not None:
        print("\n[Fast Local Decision]")
        print(json.dumps(fast_result, indent=4))
        return fast_result

    # ============================================================
    # OLLAMA AI FALLBACK
    # ============================================================

    print("\n[AI] Sending request to Ollama...")

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            format="json"
        )

        content = response["message"]["content"]

        print("\n[AI Decision]")
        print(content)

        decision = json.loads(content)
        return decision

    except json.JSONDecodeError as error:
        print(f"[JSON Error] Invalid AI JSON: {error}")

        return {
            "type": "chat",
            "response": "I couldn't understand the requested action."
        }

    except Exception as error:
        print(f"[Ollama Error] {error}")

        return {
            "type": "chat",
            "response": "I encountered an AI processing error."
        }
    """
    Main AI router.

    Fast commands are handled locally without Ollama.
    Only commands that require AI reasoning are sent to Ollama.
    """
