from playwright.sync_api import sync_playwright
from urllib.parse import quote_plus


# ============================================================
# PERSISTENT BROWSER ENGINE
# ============================================================

_playwright = None
_browser = None
_page = None


# ============================================================
# START BROWSER
# ============================================================

def start_browser():
    global _playwright
    global _browser
    global _page

    # Browser is already running
    if _browser is not None and _page is not None:
        return _page

    try:
        print("[Browser] Starting Playwright...")

        _playwright = sync_playwright().start()

        print("[Browser] Launching Chromium...")

        _browser = _playwright.chromium.launch(
            headless=False
        )

        _page = _browser.new_page()

        print("[Browser] Browser ready.")

        return _page

    except Exception as error:
        print(f"[Browser Error] Could not start browser: {error}")

        _playwright = None
        _browser = None
        _page = None

        return None


# ============================================================
# GET CURRENT PAGE
# ============================================================

def get_browser_page():
    global _page

    if _page is None:
        return start_browser()

    return _page


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

    try:
        if _browser is not None:
            _browser.close()

        if _playwright is not None:
            _playwright.stop()

        _page = None
        _browser = None
        _playwright = None

        return "Browser closed."

    except Exception as error:
        _page = None
        _browser = None
        _playwright = None

        return f"Browser close error: {error}"

    # ============================================================
# FIND ELEMENT
# ============================================================

def find_element(target):
    """
    Find an element on the current webpage.

    The target can be a visible text, button name,
    placeholder, label, or common element description.
    """

    if not target:
        return {
            "success": False,
            "error": "Element description was not provided."
        }

    try:
        page = get_browser_page()

        if page is None:
            return {
                "success": False,
                "error": "Could not start the browser."
            }

        target = target.strip()

        print(f"[Browser] Finding element: {target}")

        # ----------------------------------------------------
        # 1. Try visible text
        # ----------------------------------------------------

        locator = page.get_by_text(
            target,
            exact=True
        )

        if locator.count() > 0:
            element = locator.first

            return {
                "success": True,
                "found": True,
                "target": target,
                "element_type": "text",
                "text": element.inner_text(),
            }

        # ----------------------------------------------------
        # 2. Try button
        # ----------------------------------------------------

        locator = page.get_by_role(
            "button",
            name=target
        )

        if locator.count() > 0:
            element = locator.first

            return {
                "success": True,
                "found": True,
                "target": target,
                "element_type": "button",
                "text": element.inner_text(),
            }

        # ----------------------------------------------------
        # 3. Try link
        # ----------------------------------------------------

        locator = page.get_by_role(
            "link",
            name=target
        )

        if locator.count() > 0:
            element = locator.first

            return {
                "success": True,
                "found": True,
                "target": target,
                "element_type": "link",
                "text": element.inner_text(),
            }

        # ----------------------------------------------------
        # 4. Try placeholder
        # ----------------------------------------------------

        locator = page.get_by_placeholder(target)

        if locator.count() > 0:
            return {
                "success": True,
                "found": True,
                "target": target,
                "element_type": "input",
                "placeholder": target,
            }

        # ----------------------------------------------------
        # Element not found
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
            "error": str(error)
        }
