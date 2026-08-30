import time
import re
from brain.ollama_brain import ask_ai
from security.permissions import (
    ask_confirmation,
    authorize_path,
    requires_confirmation,
)
from tools.apps import close_application, open_application
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
    take_screenshot
)

from tools.screen import (
    get_screen_size,
    take_screen_screenshot
)

from tools.vision import analyze_screen
from tools.windows import get_active_window
from tools.windows import get_work_context

# ============================================================
# TOOL EXECUTOR
# ============================================================

def execute_tool(tool_name, args):

    if not isinstance(args, dict):
        return "Security blocked the operation: invalid arguments."

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
        query = args.get("query", "").strip()
        if not query:
            return "Google search query was not provided."

        return google_search(query)

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
    elif tool_name == "find_element":
        target = args.get("target", "").strip()

        if not target:
            return "Element description was not provided."

        return find_element(target)
    
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

    elif tool_name == "locate_and_click":
        target = args.get("target", "")
        if not target:
            return "Target element description was not provided."

        # 1. Take fresh screenshot
        screenshot_path = r"E:\hammu_screen.png"
        take_screen_screenshot(screenshot_path)

        # 2. Query vision module for coordinates
        from tools.vision import locate_element_coordinates
        coord_result = locate_element_coordinates(target, screenshot_path)

        if not coord_result.get("success"):
            return f"Vision tracking failed: {coord_result.get('error')}"

        # 3. Move and Click
        x, y = coord_result["x"], coord_result["y"]
        move_mouse(x, y)
        return click_mouse(button="left", clicks=1)


# ========================================================
# SCREENSHOT
# ========================================================

    elif tool_name == "take_screenshot":

        path = args.get(
        "path",
        "E:\\hammu_screenshot.png"
    )

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


# ============================================================
# MAIN PROGRAM
# ============================================================


def main():

    print("=" * 60)
    print("Hammu AI Assistant")
    print("=" * 60)

    while True:

        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "stop"]:
            print("Assistant: Goodbye!")
            break

        # ====================================================
        # AI DECISION
        # ====================================================

        ai_start = time.perf_counter()

        decision = ask_ai(user_input)

        ai_end = time.perf_counter()

        print(
            f"[AI Response Time] "
            f"{ai_end - ai_start:.2f} seconds"
        )

        # ====================================================
        # NORMAL CHAT
        # ====================================================

        if decision.get("type") == "chat":

            print(
                "Assistant:",
                decision.get(
                    "response",
                    "I don't have a response."
                )
            )

            continue

        # ====================================================
        # TOOL ACTION (MULTI-STEP PLAN)
        # ====================================================

        elif decision.get("type") == "plan":

            steps = decision.get("steps", [])

            if not steps:
                print(
                    "Assistant: "
                    "I couldn't determine the required actions."
                )
                continue

            final_result = ""

            for step in steps:

                tool_name = step.get("tool")
                args = step.get("args", {})

                if not tool_name:
                    print("Assistant: Invalid tool step.")
                    continue

                print(
                    f"\n[Executing Plan Step] "
                    f"{tool_name}"
                )

                result = execute_tool(
                    tool_name,
                    args
                )

                print(
                    f"[Step Result] {result}"
                )

                final_result = result

            print(
                f"Assistant: {final_result}"
            )

            continue

        # ====================================================
        # TOOL ACTION (SINGLE STEP)
        # ====================================================

        elif decision.get("type") == "tool":

            tool_name = decision.get("tool")
            args = decision.get("args", {})

            if not tool_name:
                print("Assistant: Invalid tool.")
                continue

            print(
                f"\n[Executing Tool] "
                f"{tool_name}"
            )

            result = execute_tool(
                tool_name,
                args
            )

            # ------------------------------------------------
            # SCREEN / VISION
            # ------------------------------------------------

            if (
                tool_name == "analyze_screen"
                and isinstance(result, dict)
            ):

                if result.get("success"):

                    print(
                        f"Assistant: "
                        f"{result.get('answer', '')}"
                    )

                else:

                    print(
                        f"Assistant: Vision error: "
                        f"{result.get('error', 'Unknown error')}"
                    )

            # ------------------------------------------------
            # ACTIVE WINDOW
            # ------------------------------------------------

            elif (
                tool_name == "get_active_window"
                and isinstance(result, dict)
            ):

                if result.get("success"):

                    application = result.get(
                        "application",
                        "Unknown application"
                    )

                    title = result.get(
                        "title",
                        "Unknown window"
                    )

                    print(
                        f"Assistant: "
                        f"{application} is currently open."
                    )

                    print(
                        f"Window: {title}"
                    )

                else:

                    print(
                        f"Assistant: "
                        f"Could not determine "
                        f"the active window. "
                        f"{result.get('error', 'Unknown error')}"
                    )

            # ------------------------------------------------
            # WORK CONTEXT
            # ------------------------------------------------

            elif tool_name == "get_work_context" and isinstance(result, dict):
                if result.get("success"):

                    application = result.get(
                        "application",
                        "Unknown application"
                    )

                    file_name = result.get(
                        "file",
                        "Unknown"
                    )

                    project = result.get(
                        "project",
                        "Unknown"
                    )

                    print(
                        f"Assistant: You're working in {application}."
                    )

                    print(
                        f"File: {file_name}"
                    )

                    print(
                        f"Project: {project}"
                    )

                else:

                    print(
                        f"Assistant: Could not determine "
                        f"your current work context. "
                        f"{result.get('error', 'Unknown error')}"
                    )

            # ------------------------------------------------
            # OTHER TOOLS
            # ------------------------------------------------

            else:

                print(
                    f"Assistant: {result}"
                )

            continue

        # ====================================================
        # UNKNOWN AI RESPONSE
        # ====================================================

        else:

            print(
                "Assistant: "
                "I received an unknown command format."
            )

            continue

# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()