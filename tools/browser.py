from playwright.sync_api import sync_playwright
from urllib.parse import quote_plus


# ============================================================
# PERSISTENT BROWSER ENGINE
# ============================================================

_playwright = None
_browser = None
_page = None

_pages = []
_active_page_index = 0

# ============================================================
# START BROWSER
# ============================================================

def start_browser():
    global _playwright
    global _browser
    global _page

    # Already running
    if _browser is not None and _page is not None:
        try:
            if _browser.is_connected() and not _page.is_closed():
                return _page
        except Exception:
            pass

    # Clean up stale objects
    _playwright = None
    _browser = None
    _page = None

    try:
        print("[Browser] Starting Playwright...")

        _playwright = sync_playwright().start()

        print("[Browser] Launching Chromium...")

        _browser = _playwright.chromium.launch(
            headless=False
        )

        _page = _browser.new_page()

        _pages.clear()
        _pages.append(_page)

        _active_page_index = 0

        print("[Browser] Browser ready.")

        return _page

    except Exception as error:
        print(f"[Browser Error] Could not start browser: {error}")

        try:
            if _browser is not None:
                _browser.close()
        except Exception:
            pass

        try:
            if _playwright is not None:
                _playwright.stop()
        except Exception:
            pass

        _playwright = None
        _browser = None
        _page = None

        return None


# ============================================================
# GET CURRENT PAGE
# ============================================================

def get_browser_page():
    global _page
    global _pages
    global _active_page_index

    if _browser is None:
        print("[Browser] No active browser. Starting...")
        return start_browser()

    try:
        if not _browser.is_connected():
            print("[Browser] Browser disconnected. Restarting...")
            close_browser()
            return start_browser()
    except Exception:
        print("[Browser] Browser connection check failed. Restarting...")
        close_browser()
        return start_browser()

    if not _pages:
        return start_browser()

    if _active_page_index >= len(_pages):
        _active_page_index = len(_pages) - 1

    _page = _pages[_active_page_index]

    try:
        if _page.is_closed():
            print("[Browser] Page was closed. Restarting...")

            _pages.pop(_active_page_index)

            if not _pages:
                _page = None
                return start_browser()

            _active_page_index = min(
                _active_page_index,
                len(_pages) - 1
            )

            _page = _pages[_active_page_index]

    except Exception:
        return start_browser()

    return _page


def browser_new_tab():
    global _page
    global _pages
    global _active_page_index

    try:
        if _browser is None:
            page = start_browser()

            if page is None:
                return "Could not start the browser."

            return "New tab opened."

        page = _browser.new_page()

        _pages.append(page)

        _active_page_index = len(_pages) - 1

        _page = page

        print(
            f"[Browser] New tab opened. "
            f"Active tab: {_active_page_index + 1}"
        )

        return "New tab opened."

    except Exception as error:
        return f"Could not open new tab: {error}"


def browser_list_tabs():
    global _pages
    global _active_page_index

    try:
        tabs = []

        for index, page in enumerate(_pages):
            if page.is_closed():
                continue

            try:
                title = page.title()
            except Exception:
                title = "Unknown"

            tabs.append({
                "tab": index + 1,
                "active": index == _active_page_index,
                "title": title,
                "url": page.url
            })

        return {
            "success": True,
            "tabs": tabs
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }

def browser_next_tab():
    global _page
    global _active_page_index

    try:
        if not _pages:
            return "No browser tabs are open."

        open_pages = [
            page for page in _pages
            if not page.is_closed()
        ]

        if not open_pages:
            return "No browser tabs are open."

        current_position = 0

        for index, page in enumerate(_pages):
            if index == _active_page_index:
                current_position = index
                break

        next_index = (current_position + 1) % len(_pages)

        while _pages[next_index].is_closed():
            next_index = (next_index + 1) % len(_pages)

        _active_page_index = next_index
        _page = _pages[next_index]

        try:
            _page.bring_to_front()
        except Exception:
            pass

        return f"Switched to tab {next_index + 1}."

    except Exception as error:
        return f"Could not switch tab: {error}"


def browser_previous_tab():
    global _page
    global _active_page_index

    try:
        if not _pages:
            return "No browser tabs are open."

        previous_index = (
            _active_page_index - 1
        ) % len(_pages)

        while _pages[previous_index].is_closed():
            previous_index = (
                previous_index - 1
            ) % len(_pages)

        _active_page_index = previous_index
        _page = _pages[previous_index]

        try:
            _page.bring_to_front()
        except Exception:
            pass

        return f"Switched to tab {previous_index + 1}."

    except Exception as error:
        return f"Could not switch tab: {error}"


def browser_close_tab():
    global _page
    global _pages
    global _active_page_index

    try:
        if not _pages:
            return "No browser tabs are open."

        page = _pages[_active_page_index]

        if not page.is_closed():
            page.close()

        _pages.pop(_active_page_index)

        if not _pages:
            _page = None
            _active_page_index = 0
            return "Tab closed. No browser tabs remain."

        if _active_page_index >= len(_pages):
            _active_page_index = len(_pages) - 1

        _page = _pages[_active_page_index]

        try:
            _page.bring_to_front()
        except Exception:
            pass

        return f"Tab closed. Active tab: {_active_page_index + 1}."

    except Exception as error:
        return f"Could not close tab: {error}"

# ============================================================
# OPEN URL
# ============================================================

def open_url(url):

    if not url:
        return "No URL was provided."

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        page = get_browser_page()

        if page is None:
            return "Could not start the browser."

        print(f"[Browser] Opening URL: {url}")

        page.goto(
            url,
            wait_until="domcontentloaded"
        )

        return f"Opened: {url}"

    except Exception as error:
        return f"Could not open URL: {error}"


# ============================================================
# GOOGLE SEARCH
# ============================================================

def google_search(query):

    if not query:
        return "Search query was not provided."

    try:
        encoded_query = quote_plus(query)

        url = (
            "https://www.google.com/search?q="
            + encoded_query
        )

        page = get_browser_page()

        if page is None:
            return "Could not start the browser."

        print(
            f"[Browser] Searching Google for: {query}"
        )

        page.goto(
            url,
            wait_until="domcontentloaded"
        )

        return f"Searching Google for: {query}"

    except Exception as error:
        return f"Google search failed: {error}"


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def youtube_search(query):

    if not query:
        return "YouTube search query was not provided."

    try:
        encoded_query = quote_plus(query)

        url = (
            "https://www.youtube.com/results?search_query="
            + encoded_query
        )

        page = get_browser_page()

        if page is None:
            return "Could not start the browser."

        print(
            f"[Browser] Searching YouTube for: {query}"
        )

        page.goto(
            url,
            wait_until="domcontentloaded"
        )

        return f"Searching YouTube for: {query}"

    except Exception as error:
        return f"YouTube search failed: {error}"


# ============================================================
# OPEN WEBSITE
# ============================================================

WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "chatgpt": "https://chatgpt.com",
    "gmail": "https://mail.google.com",
    "facebook": "https://www.facebook.com",
    "linkedin": "https://www.linkedin.com",
    "whatsapp": "https://web.whatsapp.com",
    "stackoverflow": "https://stackoverflow.com",
    "reddit": "https://www.reddit.com",
}


def open_website(name):

    if not name:
        return "Website name was not provided."

    name = name.lower().strip()

    if name not in WEBSITES:
        return (
            f"I don't have a saved website shortcut "
            f"for '{name}'."
        )

    url = WEBSITES[name]

    try:
        page = get_browser_page()

        if page is None:
            return "Could not start the browser."

        print(
            f"[Browser] Opening website: {name}"
        )

        page.goto(
            url,
            wait_until="domcontentloaded"
        )

        return f"Opened {name}."

    except Exception as error:
        return (
            f"Could not open {name}: {error}"
        )


# ============================================================
# PAGE TITLE
# ============================================================

def get_page_title():

    try:
        page = get_browser_page()

        if page is None:
            return "Could not start the browser."

        title = page.title()

        return {
            "success": True,
            "title": title
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# CURRENT URL
# ============================================================

def get_current_url():

    try:
        page = get_browser_page()

        if page is None:
            return "Could not start the browser."

        return {
            "success": True,
            "url": page.url
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# BROWSER BACK
# ============================================================

def browser_back():

    try:
        page = get_browser_page()

        if page is None:
            return "Could not start the browser."

        page.go_back(
            wait_until="domcontentloaded"
        )

        return "Went back."

    except Exception as error:
        return f"Could not go back: {error}"


# ============================================================
# BROWSER FORWARD
# ============================================================

def browser_forward():

    try:
        page = get_browser_page()

        if page is None:
            return "Could not start the browser."

        page.go_forward(
            wait_until="domcontentloaded"
        )

        return "Went forward."

    except Exception as error:
        return f"Could not go forward: {error}"


# ============================================================
# BROWSER REFRESH
# ============================================================

def browser_refresh():

    try:
        page = get_browser_page()

        if page is None:
            return "Could not start the browser."

        page.reload(
            wait_until="domcontentloaded"
        )

        return "Page refreshed."

    except Exception as error:
        return f"Could not refresh page: {error}"


# ============================================================
# CLOSE BROWSER
# ============================================================

def close_browser():
    global _playwright
    global _browser
    global _page
    global _active_page_index

    try:
        if _browser is not None:
            _browser.close()

        if _playwright is not None:
            _playwright.stop()

        _page = None
        _browser = None
        _playwright = None
        _pages.clear()
        _active_page_index = 0

        return "Browser closed."

    except Exception as error:
        _page = None
        _browser = None
        _playwright = None
        _pages.clear()
        _active_page_index = 0

        return f"Browser close error: {error}"

# ============================================================
# FIND ELEMENT
# ============================================================

def find_element(target):
    """
    Find an element on the current webpage.

    This function uses DOM information rather than
    screenshot/vision analysis.
    """

    if not target:
        return {
            "success": False,
            "found": False,
            "error": "Element target was not provided."
        }

    target = target.strip()

    try:
        page = get_browser_page()

        if page is None:
            return {
                "success": False,
                "found": False,
                "error": "Browser is not running."
            }

        print(f"[Browser] Finding element: {target}")

        # ----------------------------------------------------
        # Common semantic targets
        # ----------------------------------------------------

        target_lower = target.lower()

        # Google search box
        if target_lower in {
            "search box",
            "google search box",
            "search field",
            "search input",
        }:

            selectors = [
                'textarea[name="q"]',
                'input[name="q"]',
                'textarea[aria-label*="Search"]',
                'input[aria-label*="Search"]',
            ]

            for selector in selectors:

                locator = page.locator(selector).first

                if locator.count() > 0 and locator.is_visible():

                    return {
                        "success": True,
                        "found": True,
                        "target": target,
                        "selector": selector,
                        "tag": locator.evaluate(
                            "(element) => element.tagName"
                        ),
                        "message": "Element found."
                    }

        # ----------------------------------------------------
        # Generic text search
        # ----------------------------------------------------

        locator = page.get_by_text(
            target,
            exact=False
        ).first

        if locator.count() > 0 and locator.is_visible():

            return {
                "success": True,
                "found": True,
                "target": target,
                "message": "Element found by text."
            }

        # ----------------------------------------------------
        # Generic role-based search
        # ----------------------------------------------------

        for role in [
            "button",
            "link",
            "textbox"
        ]:

            try:

                locator = page.get_by_role(
                    role,
                    name=target,
                    exact=False
                ).first

                if locator.count() > 0 and locator.is_visible():

                    return {
                        "success": True,
                        "found": True,
                        "target": target,
                        "role": role,
                        "message": "Element found by role."
                    }

            except Exception:
                pass

        # ----------------------------------------------------
        # Nothing found
        # ----------------------------------------------------

        return {
            "success": True,
            "found": False,
            "target": target,
            "message": "No matching element was found."
        }

    except Exception as error:

        return {
            "success": False,
            "found": False,
            "target": target,
            "error": str(error)
        }
