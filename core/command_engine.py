from memory.memory import memory
from voice.text_to_speech import text_to_speech
from brain.ollama_brain import ask_ai, fast_command
from brain.context import context
from security.permissions import (
    ask_confirmation,
    authorize_path,
    requires_confirmation,
)

from tools.apps import (
    close_application,
    open_application,
)

from tools.browser import (
    google_search,
    open_url,
    open_website,
    youtube_search,
    get_page_title,
    get_current_url,
    find_element,
    browser_back,
    browser_forward,
    browser_refresh,
    close_browser,
    browser_new_tab,
    browser_close_tab,
    browser_next_tab,
    browser_previous_tab,
    browser_list_tabs,
)

from tools.chrome_profiles import (
    open_chrome_profile,
    list_chrome_profiles,
    get_current_chrome_profile,
)

from tools.files import (
    copy_item,
    create_file,
    create_folder,
    delete_file,
    delete_folder,
    get_current_directory,
    list_directory,
    move_item,
    open_folder,
    read_file,
    rename_item,
    resolve_path,
    search_files,
)

from tools.input import (
    type_text,
    press_key,
    hotkey,
    move_mouse,
    click_mouse,
    double_click,
    right_click,
    scroll_mouse,
    take_screenshot,
)

from tools.screen import (
    get_screen_size,
    take_screen_screenshot,
)

from tools.vision import analyze_screen
from tools.windows import get_active_window
from tools.windows import get_work_context

from tools.calculator import calculate


# ============================================================
# TOOL EXECUTOR
# ============================================================

def execute_tool(tool_name, args):

    if not isinstance(args, dict):
        return "Security blocked the operation: invalid arguments."

    # Calculator
    if tool_name == "calculator":

        return calculate(
            args.get("operation"),
            args.get("numbers", [])
        )


    # ========================================================
    # TOOLS THAT REQUIRE A PATH
    # ========================================================

    path_tools = {
        "create_folder",
        "open_folder",
        "list_directory",
        "create_file",
        "read_file",
        "delete_file",
        "delete_folder",
        "rename_item",
        "copy_item",
        "move_item",
        "search_files",
    }

    # ========================================================
    # DETERMINE TARGET PATHS
    # ========================================================

    paths_to_check = []

    if tool_name in {
        "create_folder",
        "open_folder",
        "list_directory",
        "create_file",
        "read_file",
        "delete_file",
        "delete_folder",
    }:
        path = args.get("path", "")
        if path:
            paths_to_check.append(path)

    elif tool_name == "rename_item":
        old_path = args.get("old_path", "")
        if old_path:
            paths_to_check.append(old_path)

    elif tool_name in {"copy_item", "move_item"}:
        source = args.get("source", "")
        destination = args.get("destination", "")

        if source:
            paths_to_check.append(source)
        if destination:
            paths_to_check.append(destination)

    elif tool_name == "search_files":
        location = args.get("location", "")
        if location:
            paths_to_check.append(location)

    # ========================================================
    # SECURITY CHECK
    # ========================================================

    for path in paths_to_check:
        resolved_path = resolve_path(path)
        allowed, message = authorize_path(resolved_path)

        if not allowed:
            return message

    # ========================================================
    # CONFIRMATION FOR DANGEROUS ACTIONS
    # ========================================================

    if requires_confirmation(tool_name):
        target = (
            args.get("path")
            or args.get("source")
            or args.get("old_path")
            or "system operation"
        )

        if not ask_confirmation(tool_name, target):
            return "Operation cancelled by user."

    # ========================================================
    # APPLICATION TOOLS
    # ========================================================

    if tool_name == "open_application":
        name = args.get("name", "").strip()
        if not name:
            return "Application name was not provided."
        return open_application(name)

    elif tool_name == "close_application":
        name = args.get("name", "").strip()
        if not name:
            return "Application name was not provided."
        return close_application(name)

    # ========================================================
    # FOLDER TOOLS
    # ========================================================

    elif tool_name == "create_folder":
        path = args.get("path", "").strip()
        if not path:
            path = args.get("name", "").strip()

        if not path:
            return "Folder path was not provided."

        return create_folder(path)

    elif tool_name == "open_folder":
        path = args.get("path", "").strip()
        if not path:
            return "Folder path was not provided."

        return open_folder(path)

    elif tool_name == "list_directory":
        path = args.get("path", "").strip()
        return list_directory(path)

    # ========================================================
    # FILE TOOLS
    # ========================================================

    elif tool_name == "create_file":
        path = args.get("path", "").strip()
        content = args.get("content", "")

        if not path:
            return "File path was not provided."

        return create_file(path, content)

    elif tool_name == "read_file":
        path = args.get("path", "").strip()
        if not path:
            return "File path was not provided."

        return read_file(path)

    elif tool_name == "rename_item":
        old_path = args.get("old_path", "").strip()
        new_name = args.get("new_name", "").strip()

        if not old_path or not new_name:
            return "Both old_path and new_name are required."

        return rename_item(old_path, new_name)

    elif tool_name == "copy_item":
        source = args.get("source", "").strip()
        destination = args.get("destination", "").strip()

        if not source or not destination:
            return "Both source and destination are required."

        return copy_item(source, destination)

    elif tool_name == "move_item":
        source = args.get("source", "").strip()
        destination = args.get("destination", "").strip()

        if not source or not destination:
            return "Both source and destination are required."

        return move_item(source, destination)

    # ========================================================
    # DELETE
    # ========================================================

    elif tool_name == "delete_file":
        path = args.get("path", "").strip()
        if not path:
            return "File path was not provided."

        return delete_file(path)

    elif tool_name == "delete_folder":
        path = args.get("path", "").strip()
        if not path:
            return "Folder path was not provided."

        return delete_folder(path)

    # ========================================================
    # CURRENT DIRECTORY
    # ========================================================

    elif tool_name == "get_current_directory":
        return get_current_directory()

    # ========================================================
    # SEARCH
    # ========================================================

    elif tool_name == "search_files":
        search_term = args.get("search_term", "").strip()
        location = args.get("location", "").strip()

        if not search_term:
            return "Search term was not provided."

        return search_files(search_term, location)

    # ========================================================
    # BROWSER TOOLS
    # ========================================================

    elif tool_name == "open_url":
        url = args.get("url", "").strip()
        if not url:
            return "URL was not provided."

        return open_url(url)

    elif tool_name == "google_search":
        result = google_search(args["query"])

        if isinstance(result, dict) and result.get("success"):
            context.save_search(
                engine="google",
                query=args["query"],
                results=result.get("results", [])
            )

        return result

    elif tool_name == "youtube_search":
        query = args.get("query", "").strip()
        if not query:
            return "YouTube search query was not provided."

        return youtube_search(query)

    elif tool_name == "open_website":
        name = args.get("name", "").strip()
        if not name:
            return "Website name was not provided."

        return open_website(name)
    
    elif tool_name == "close_browser":
        return close_browser()

    elif tool_name == "get_page_title":
        return get_page_title()

    elif tool_name == "get_current_url":
        return get_current_url()

    elif tool_name == "browser_back":
        return browser_back()

    elif tool_name == "browser_forward":
        return browser_forward()

    elif tool_name == "browser_refresh":
        return browser_refresh()

    elif tool_name == "browser_new_tab":
        url = args.get("url")
        return browser_new_tab(url)

    elif tool_name == "browser_close_tab":
        return browser_close_tab()

    elif tool_name == "browser_next_tab":
        return browser_next_tab()

    elif tool_name == "browser_previous_tab":
        return browser_previous_tab()

    elif tool_name == "browser_list_tabs":
        return browser_list_tabs()
    
# ========================================================
# BROWSER STATE
# ========================================================

    elif tool_name == "get_page_title":
        return get_page_title()

    elif tool_name == "get_current_url":
        return get_current_url()

    elif tool_name == "browser_back":
        return browser_back()

    elif tool_name == "browser_forward":
        return browser_forward()

    elif tool_name == "browser_refresh":
        return browser_refresh()

    elif tool_name == "close_browser":
        return close_browser()

# ========================================================
# BROWSER DOM
# ========================================================

    elif tool_name == "find_element":

        target = args.get(
            "target",
            ""
        ).strip()

        if not target:
            return "Element target was not provided."

        return find_element(target)
    
    elif tool_name == "open_chrome_profile":

        profile_name = args.get(
            "profile_name",
            ""
        ).strip()

        if not profile_name:
            return "Chrome profile name was not provided."

        result = open_chrome_profile(profile_name)

        if not result.get("success"):
            return result.get(
                "error",
                "Could not open Chrome profile."
            )

        return result.get(
            "message",
            f"Opened Chrome profile '{profile_name}'."
        )

    elif tool_name == "get_current_chrome_profile":
        return get_current_chrome_profile()
    
# ========================================================
# KEYBOARD
# ========================================================

    elif tool_name == "type_text":

        text = args.get(
        "text",
        ""
    )

        return type_text(text)


    elif tool_name == "press_key":

        key = args.get(
        "key",
        ""
    )

        return press_key(key)


    elif tool_name == "hotkey":

        keys = args.get(
        "keys",
        []
    )

        return hotkey(keys)


# ========================================================
# MOUSE
# ========================================================

    elif tool_name == "move_mouse":
        x = args.get("x")
        y = args.get("y")

        if x is None or y is None:
            return "Mouse coordinates were not provided."

        return move_mouse(x, y)


    elif tool_name == "click_mouse":
        button = args.get("button", "left")
        clicks = args.get("clicks", 1)

        return click_mouse(
            button=button,
            clicks=clicks
        )


    elif tool_name == "double_click":
        x = args.get("x")
        y = args.get("y")

        if x is not None and y is not None:
            move_mouse(x, y)

        return double_click()


    elif tool_name == "right_click":
        x = args.get("x")
        y = args.get("y")

        if x is not None and y is not None:
            move_mouse(x, y)

        return right_click()


    elif tool_name == "scroll_mouse":
        amount = args.get("amount", 0)

        return scroll_mouse(amount)


    elif tool_name == "locate_and_click":
        target = args.get("target", "")

        if not target:
            return "Target element description was not provided."

        # 1. Take fresh screenshot
        screenshot_path = r"E:\hammu_screen.png"
        take_screen_screenshot(screenshot_path)

        # 2. Query vision module for coordinates
        from tools.vision import locate_element_coordinates

        coord_result = locate_element_coordinates(
            target,
            screenshot_path
        )

        if not coord_result.get("success"):
            return (
                f"Vision tracking failed: "
                f"{coord_result.get('error')}"
            )

        # 3. Move and click
        x = coord_result["x"]
        y = coord_result["y"]

        move_mouse(x, y)

        return click_mouse(
            button="left",
            clicks=1
        )


# ========================================================
# SCREENSHOT
# ========================================================

    elif tool_name == "take_screenshot":

        path = args.get(
            "path",
            "E:\\hammu_screenshot.png"
        )

        resolved_path = resolve_path(path)

        if resolved_path.exists() and resolved_path.is_dir():

            counter = 1

            while True:

                screenshot_path = (
                    resolved_path /
                    f"hammu_screenshot_{counter:03d}.png"
                )

                if not screenshot_path.exists():
                    break

                counter += 1

            path = str(screenshot_path)

        return take_screenshot(path)
    
    elif tool_name == "get_screen_size":

        return get_screen_size()

    elif tool_name == "take_screen_screenshot":

        path = args.get(
        "path",
        "E:\\hammu_screen.png"
    )

        return take_screen_screenshot(
        path
    )

    elif tool_name == "analyze_screen":

        question = args.get(
        "question",
        "Describe what is currently visible on the screen."
    )

        screenshot_path = args.get(
        "path",
        r"E:\hammu_screen.png"
    )

    # Take a fresh screenshot first
        screenshot_result = take_screen_screenshot(
        screenshot_path
    )

    # If screenshot failed, don't send anything to vision model
        if isinstance(screenshot_result, dict):
            if screenshot_result.get("success") is False:
                return screenshot_result

    # Analyze the fresh screenshot
        return analyze_screen(
        screenshot_path,
        question
    )

# ========================================================
# WINDOWS / ACTIVE WINDOW
# ========================================================

    elif tool_name == "get_active_window":
        result = get_active_window()

        if not result.get("success"):
            return result.get(
                "error",
                "Could not determine the active window."
            )

        application = result.get(
            "application",
            "Unknown application"
        )

        title = result.get(
            "title",
            "Unknown window"
        )

        return {
            "success": True,
            "application": application,
            "title": title
        }
    
    elif tool_name == "get_work_context":
        return get_work_context()
        
# ========================================================
# UNKNOWN TOOL
# ========================================================

    else:
        return f"Unknown tool: {tool_name}"


def handle_context_command(user_input):
    """
    Handle commands that refer to previous Google search results.

    Examples:
        open the first result
        open result 3
        open 3rd
        open 1st and 3rd
        open all
    """

    text = user_input.lower().strip()

    if not text:
        return None

    # --------------------------------------------------------
    # Make sure we actually have previous search results
    # --------------------------------------------------------

    if not context.last_search_results:
        return None

    # --------------------------------------------------------
    # Result number patterns
    # --------------------------------------------------------

    result_patterns = {
        "first": 1,
        "1st": 1,

        "second": 2,
        "2nd": 2,

        "third": 3,
        "3rd": 3,

        "fourth": 4,
        "4th": 4,

        "fifth": 5,
        "5th": 5,

        "sixth": 6,
        "6th": 6,

        "seventh": 7,
        "7th": 7,

        "eighth": 8,
        "8th": 8,

        "ninth": 9,
        "9th": 9,

        "tenth": 10,
        "10th": 10,
    }

    # --------------------------------------------------------
    # Check whether this is an "open result" command
    # --------------------------------------------------------

    open_words = (
        "open",
        "show",
        "visit",
        "go to",
    )

    if not any(word in text for word in open_words):
        return None

    # --------------------------------------------------------
    # OPEN ALL RESULTS
    # --------------------------------------------------------

    if "all" in text:
        return {
            "type": "tool",
            "tool": "open_search_results",
            "args": {}
        }

    # --------------------------------------------------------
    # Find requested result number(s)
    # --------------------------------------------------------

    result_numbers = []

    for word, number in result_patterns.items():
        if word in text and number not in result_numbers:
            result_numbers.append(number)

    # Nothing recognized
    if not result_numbers:
        return None

    # --------------------------------------------------------
    # Validate result numbers
    # --------------------------------------------------------

    valid_numbers = [
        number
        for number in result_numbers
        if context.get_search_result(number) is not None
    ]

    if not valid_numbers:
        return {
            "type": "chat",
            "response": "I don't have those search results available."
        }

    # --------------------------------------------------------
    # ONE RESULT
    # --------------------------------------------------------

    if len(valid_numbers) == 1:
        result_number = valid_numbers[0]
        result = context.get_search_result(result_number)

        return {
            "type": "tool",
            "tool": "open_url",
            "args": {
                "url": result["url"]
            }
        }

    # --------------------------------------------------------
    # MULTIPLE RESULTS
    # --------------------------------------------------------

    return {
        "type": "tool",
        "tool": "open_search_results",
        "args": {
            "numbers": valid_numbers
        }
    }

def speak_response(text):
    if text:
        text_to_speech.speak(text)

def handle_memory_command(user_input):
    text = user_input.strip() 
    lower_text = text.lower()

    if lower_text.startswith("remember that "): 

        memory_text = text[len("remember that "):].strip() 

        if not memory_text: 

            return { "success": False, "type": "tool", "result": "What would you like me to remember?" }
        
        memory.remember(memory_text) 
        return { "success": True, "type": "tool", "result": f"I'll remember that {memory_text}." } 

    if lower_text in [
        "what do you remember",
        "what do you remember?",
        "show my memories",
        "show my memory",
        "recall my memories"
    ]:
        memories = memory.recall()

        if not memories:
            return {
                "success": True,
                "type": "tool",
                "result": "I don't have any memories saved yet."
            }

        memory_text = "\n".join(
            f"{memory_id}. {memory_value}"
            for memory_id, memory_value in memories
        )

        return {
            "success": True,
            "type": "tool",
            "result": f"Here is what I remember:\n{memory_text}"
        }
    
    if lower_text.startswith("what do you remember about "):
        keyword = text[len("what do you remember about "):].strip()

        if not keyword:
            return {
                "success": False,
                "type": "tool",
                "result": "What would you like me to remember?"
            }

        memories = memory.search(keyword)

        if not memories:
            return {
                "success": True,
                "type": "tool",
                "result": f"I don't have any memories about {keyword}."
            }

        memory_text = "\n".join(
            f"{memory_id}. {memory_value}"
            for memory_id, memory_value in memories
        )

        return {
            "success": True,
            "type": "tool",
            "result": f"Here is what I remember about {keyword}:\n{memory_text}"
        }
    
    if lower_text.startswith("what do you remember about "):

        keyword = text[len("what do you remember about "):].strip()

        if not keyword:
            return {
                "success": False,
                "type": "tool",
                "result": "What would you like me to remember?"
            }

        memories = memory.search(keyword)

        if not memories:
            return {
                "success": True,
                "type": "tool",
                "result": f"I don't have any memories about {keyword}."
            }

        memory_text = "\n".join(
            f"{memory_id}. {memory_value}"
            for memory_id, memory_value in memories
        )

        return {
            "success": True,
            "type": "tool",
            "result": f"Here is what I remember about {keyword}:\n{memory_text}"
        }
    
    if lower_text.startswith("what is my favourite "):

        keyword = text[len("what is my favourite "):].strip()

        if not keyword:
            return {
                "success": False,
                "type": "tool",
                "result": "What would you like to know?"
            }

        memories = memory.search(
            f"favourite {keyword}"
        )

        if not memories:
            return {
                "success": True,
                "type": "tool",
                "result": f"I don't have any memories about your favourite {keyword}."
            }

        memory_value = memories[0][1]

        prefix = f"my favourite {keyword} is "

        if memory_value.lower().startswith(prefix):
            favourite_value = memory_value[len(prefix):].strip()
        else:
            favourite_value = memory_value

        return {
            "success": True,
            "type": "tool",
            "result": f"Your favourite {keyword} is {favourite_value}."
        }
        
    return None

def _process_command(user_input):
    """
    Process one HAMMU command.

    This function is independent of the user interface.
    Console, voice, and GUI can all use it.
    """

    memory_result = handle_memory_command(user_input)

    if memory_result is not None:
        # speak_response(
        #     memory_result.get("result", "")
        # )
        return memory_result

    decision = handle_context_command(user_input)

    if decision is None:
        decision = fast_command(user_input)

    if decision is None:
        decision = ask_ai(user_input)

    if not isinstance(decision, dict):
        return {
            "success": False,
            "type": "chat",
            "response": "I couldn't understand the command."
        }

    decision_type = decision.get("type")

    # --------------------------------------------
    # CHAT
    # --------------------------------------------

    if decision_type == "chat":
        response = decision.get(
            "response",
            "I don't have a response."
        )

        # speak_response(response)

        return {
            "success": True,
            "type": "chat",
            "response": response
        }

    # --------------------------------------------
    # SINGLE TOOL
    # --------------------------------------------

    if decision_type == "tool":

        tool_name = decision.get("tool")
        args = decision.get("args", {})

        if not tool_name:

            return {
                "success": False,
                "type": "error",
                "response": "Invalid tool."
            }

        result = execute_tool(tool_name, args)

        return {
            "success": True,
            "type": "tool",
            "tool": tool_name,
            "result": result
        }

    # --------------------------------------------
    # MULTI-STEP PLAN
    # --------------------------------------------

    if decision_type == "plan":

        steps = decision.get("steps", [])

        if not steps:

            return {
                "success": False,
                "type": "error",
                "response": "I couldn't determine the required actions."
            }

        results = []

        for step in steps:

            tool_name = step.get("tool")
            args = step.get("args", {})

            if not tool_name:

                results.append({
                    "success": False,
                    "error": "Invalid tool step."
                })

                continue

            result = execute_tool(
                tool_name,
                args
            )

            results.append({
                "tool": tool_name,
                "result": result
            })

        return {
            "success": True,
            "type": "plan",
            "results": results
        }

    # --------------------------------------------
    # UNKNOWN
    # --------------------------------------------

    return {
        "success": False,
        "type": "error",
        "response": "I received an unknown command format."
    }


# ============================================================
# CONVERSATION HISTORY
# ============================================================

def process_command(user_input):
    """
    Public command processor.

    Runs the normal HAMMU command engine and then
    stores the completed interaction in short-term context.
    """

    result = _process_command(user_input)

    # Save user's message
    if user_input:
        context.add_user_message(user_input)

    # Save HAMMU's response
    if isinstance(result, dict):

        response = (
            result.get("response")
            or result.get("result")
        )

        if response:
            if isinstance(response, dict):
                response = str(response)

            context.add_assistant_message(response)

    return result