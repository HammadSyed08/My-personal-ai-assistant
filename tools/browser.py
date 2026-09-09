from playwright.sync_api import sync_playwright
from urllib.parse import quote_plus

import os
import subprocess
import time
import urllib.request


# ============================================================
# PERSISTENT BROWSER ENGINE
# ============================================================

_playwright = None
_browser = None
_context = None
_page = None

_pages = []
_active_page_index = 0

# ============================================================
# HAMMU CHROME CONFIGURATION
# ============================================================

HAMMU_CHROME_PORT = 9222

HAMMU_CHROME_DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "hammu_chrome"
)

CHROME_PATHS = [
    os.path.expandvars(
        r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"
    ),
    os.path.expandvars(
        r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"
    ),
    os.path.expandvars(
        r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
    ),
]

# ============================================================
# NAVIGATION HELPER
# ============================================================

def navigate_page(page, url, timeout=15000):
    """
    Navigate to a URL without waiting for the entire page
    to finish loading.

    Modern websites can keep loading resources indefinitely,
    so we only wait until navigation is committed.
    """
    try:
        page.goto(
            url,
            wait_until="commit",
            timeout=timeout
        )

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
# FIND CHROME
# ============================================================

def get_chrome_executable():
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path

    return None


# ============================================================
# CHECK CHROME CDP
# ============================================================

def chrome_cdp_available():
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{HAMMU_CHROME_PORT}/json/version",
            timeout=1
        ) as response:

            return response.status == 200

    except Exception:
        return False


# ============================================================
# START HAMMU CHROME AUTOMATICALLY
# ============================================================

def start_hammu_chrome():
    """
    Start a dedicated persistent Chrome instance for HAMMU.

    This does NOT touch the user's normal Chrome profile.
    """

    # --------------------------------------------------------
    # Chrome is already running on our CDP port
    # --------------------------------------------------------

    if chrome_cdp_available():
        print(
            f"[Browser] Chrome already running on "
            f"port {HAMMU_CHROME_PORT}."
        )

        return True

    # --------------------------------------------------------
    # Find Chrome executable
    # --------------------------------------------------------

    chrome_path = get_chrome_executable()

    if not chrome_path:
        print("[Browser Error] Google Chrome was not found.")
        return False

    # --------------------------------------------------------
    # Create persistent HAMMU Chrome directory
    # --------------------------------------------------------

    os.makedirs(
        HAMMU_CHROME_DATA,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Build Chrome command
    # --------------------------------------------------------

    chrome_command = [
        chrome_path,

        f"--remote-debugging-port={HAMMU_CHROME_PORT}",

        f"--user-data-dir={HAMMU_CHROME_DATA}",

        "--remote-allow-origins=http://localhost",

        "--no-first-run",

        "--no-default-browser-check",
    ]

    # --------------------------------------------------------
    # Start Chrome
    # --------------------------------------------------------

    try:

        print("[Browser] HAMMU Chrome is not running.")
        print("[Browser] Starting HAMMU Chrome...")
        print(
            f"[Browser] Data directory: "
            f"{HAMMU_CHROME_DATA}"
        )

        subprocess.Popen(
            chrome_command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    except Exception as error:

        print(
            f"[Browser Error] Could not start Chrome: {error}"
        )

        return False

    # --------------------------------------------------------
    # Wait for CDP
    # --------------------------------------------------------

    print(
        f"[Browser] Waiting for Chrome on "
        f"port {HAMMU_CHROME_PORT}..."
    )

    for _ in range(30):

        if chrome_cdp_available():

            print(
                "[Browser] Chrome remote debugging is ready."
            )

            return True

        time.sleep(0.5)

    print(
        "[Browser Error] Chrome started, "
        "but CDP did not become available."
    )

    return False

# ============================================================
# START BROWSER
# ============================================================


def start_browser():
    global _playwright
    global _browser
    global _context
    global _page
    global _pages
    global _active_page_index

    # ========================================================
    # BROWSER ALREADY CONNECTED
    # ========================================================

    if (
        _browser is not None
        and _context is not None
        and _page is not None
    ):
        try:

            if (
                _browser.is_connected()
                and not _page.is_closed()
            ):
                return _page

        except Exception:
            pass

    # ========================================================
    # RESET OLD STATE
    # ========================================================

    _playwright = None
    _browser = None
    _context = None
    _page = None
    _pages = []
    _active_page_index = 0

    try:

        # ====================================================
        # START CHROME AUTOMATICALLY
        # ====================================================

        if not chrome_cdp_available():

            if not start_hammu_chrome():

                return None

        # ====================================================
        # START PLAYWRIGHT
        # ====================================================

        print("[Browser] Starting Playwright...")

        _playwright = sync_playwright().start()

        # ====================================================
        # CONNECT TO HAMMU CHROME
        # ====================================================

        print(
            f"[Browser] Connecting to Chrome on "
            f"port {HAMMU_CHROME_PORT}..."
        )

        _browser = _playwright.chromium.connect_over_cdp(
            f"http://127.0.0.1:{HAMMU_CHROME_PORT}"
        )

        print("[Browser] Connected to Chrome.")

        # ====================================================
        # GET CONTEXT
        # ====================================================

        contexts = _browser.contexts

        if not contexts:

            print("[Browser] No Chrome context found.")

            return None

        _context = contexts[0]

        # ====================================================
        # GET EXISTING TABS
        # ====================================================

        _pages = [
            page
            for page in _context.pages
            if not page.is_closed()
        ]

        # ====================================================
        # CREATE FIRST TAB IF NECESSARY
        # ====================================================

        if not _pages:

            print("[Browser] No tabs found. Creating one...")

            _page = _context.new_page()

            _pages = [_page]

        else:

            _page = _pages[0]

        _active_page_index = 0

        # ====================================================
        # BRING HAMMU TAB TO FRONT
        # ====================================================

        try:
            _page.bring_to_front()
        except Exception:
            pass

        print(
            f"[Browser] Connected to Chrome with "
            f"{len(_pages)} tab(s)."
        )

        print("[Browser] Browser ready.")

        return _page

    except Exception as error:

        print(
            f"[Browser Error] Could not start browser: {error}"
        )

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
        _context = None
        _page = None
        _pages = []
        _active_page_index = 0

        return None


# ============================================================
# GET CURRENT PAGE
# ============================================================

def get_browser_page():
    global _browser
    global _context
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


# ============================================================
# NEW TAB
# ============================================================

def browser_new_tab(url=None):
    global _browser
    global _context
    global _page
    global _pages
    global _active_page_index

    try:
        page = get_browser_page()

        if page is None:
            return {
                "success": False,
                "error": "Could not start the browser."
            }

        # Make sure the browser context exists
        if _context is None:
            return {
                "success": False,
                "error": "Browser context is not running."
            }

        print("[Browser] Opening new tab...")

        # IMPORTANT:
        # Create the new page inside the SAME context.
        # This makes it a new tab instead of a separate window.
        new_page = _context.new_page()

        _pages.append(new_page)

        _active_page_index = len(_pages) - 1

        _page = new_page

        if url:
            url = url.strip()

            if not url.startswith(
                ("http://", "https://")
            ):
                url = "https://" + url

            print(
                f"[Browser] Opening URL in new tab: {url}"
            )

            result = navigate_page(new_page, url)

            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"]
                }

        try:
            new_page.bring_to_front()
        except Exception:
            pass

        return {
            "success": True,
            "message": "New tab opened.",
            "tab": _active_page_index + 1,
            "url": new_page.url
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


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

        try:
            page.goto(
                url,
                wait_until="commit",
                timeout=15000
            )
        except Exception as error:
            # Chrome/CDP can occasionally report a connection
            # close even though navigation has started.
            print(
                f"[Browser] Navigation warning: {error}"
            )

        return {
            "success": True,
            "message": f"Opened: {url}",
            "url": page.url
        }

    except Exception as error:
        return {
            "success": False,
            "error": f"Could not open URL: {error}"
        }



# ============================================================
# GOOGLE SEARCH
# ============================================================


def resolve_google_url(page, google_url):
    """
    Resolve a Google /goto tracking URL to its final destination.
    """

    if not google_url:
        return None

    if "/goto?" not in google_url:
        return google_url

    try:
        original_url = page.url

        # Open the Google redirect in a temporary tab.
        new_page = page.context.new_page()

        try:
            new_page.goto(
                google_url,
                wait_until="commit",
                timeout=10000
            )

            new_page.wait_for_timeout(1500)

            final_url = new_page.url

            print(
                f"[Browser] Google redirect resolved:"
                f"\n    From: {google_url}"
                f"\n    To:   {final_url}"
            )

            return final_url

        finally:
            try:
                new_page.close()
            except Exception:
                pass

    except Exception as error:

        print(
            f"[Browser] Could not resolve Google URL: "
            f"{error}"
        )

        return google_url
def google_search(query):
    """
    Search Google using the persistent HAMMU Chrome browser.

    Returns structured search results that can later be used
    by the browser-context system for commands such as:

        "open the first result"
        "open result 2"
    """

    if not query:
        return {
            "success": False,
            "error": "Search query was not provided."
        }

    try:
        # --------------------------------------------------------
        # BUILD GOOGLE SEARCH URL
        # --------------------------------------------------------

        encoded_query = quote_plus(query)

        url = (
            "https://www.google.com/search?q="
            + encoded_query
        )

        # --------------------------------------------------------
        # GET ACTIVE BROWSER PAGE
        # --------------------------------------------------------

        page = get_browser_page()

        if page is None:
            return {
                "success": False,
                "error": "Could not start the browser."
            }

        print(
            f"[Browser] Searching Google for: {query}"
        )

        # --------------------------------------------------------
        # NAVIGATE
        # --------------------------------------------------------

        navigation = navigate_page(
            page,
            url,
            timeout=15000
        )

        if not navigation["success"]:
            print(
                "[Browser] Navigation warning:",
                navigation["error"]
            )

        # --------------------------------------------------------
        # WAIT FOR GOOGLE PAGE
        # --------------------------------------------------------

        print(
            "[Browser] Waiting for Google search page..."
        )

        try:
            page.wait_for_timeout(2000)
        except Exception:
            pass

        # --------------------------------------------------------
        # DEBUG PAGE STATE
        # --------------------------------------------------------

        try:
            print(
                "[Browser Debug] Current URL:",
                page.url
            )

            print(
                "[Browser Debug] Page title:",
                page.title()
            )

        except Exception as error:

            print(
                f"[Browser Debug] Page information failed: {error}"
            )

        # --------------------------------------------------------
        # WAIT FOR SEARCH RESULTS
        # --------------------------------------------------------

        result_selectors = [
            "div.MjjYud h3",
            "div.g h3",
            "h3"
        ]

        result_selector_found = None

        for selector in result_selectors:

            try:

                print(
                    f"[Browser] Checking selector: {selector}"
                )

                page.wait_for_selector(
                    selector,
                    timeout=5000,
                    state="visible"
                )

                locator = page.locator(selector)

                if locator.count() > 0:

                    result_selector_found = selector

                    print(
                        "[Browser] Result selector found:",
                        selector
                    )

                    break

            except Exception:
                continue

        if result_selector_found is None:

            print(
                "[Browser] Google results were not detected."
            )

        # --------------------------------------------------------
        # EXTRA RENDERING TIME
        # --------------------------------------------------------

        try:
            page.wait_for_timeout(1500)
        except Exception:
            pass

        # --------------------------------------------------------
        # DEBUG PAGE TEXT
        # --------------------------------------------------------

        try:

            body_text = page.locator(
                "body"
            ).inner_text()

            print(
                "[Browser Debug] Page text preview:"
            )

            print(
                body_text[:3000]
            )

        except Exception as error:

            print(
                f"[Browser Debug] Could not read page text: {error}"
            )

        # --------------------------------------------------------
        # EXTRACT RESULTS
        # --------------------------------------------------------

        results = []

        try:

            if result_selector_found:

                headings = page.locator(
                    result_selector_found
                )

            else:

                headings = page.locator(
                    "h3"
                )

            heading_count = headings.count()

            print(
                f"[Browser] h3 elements detected: "
                f"{heading_count}"
            )

            for i in range(
                min(heading_count, 20)
            ):

                try:

                    heading = headings.nth(i)

                    if not heading.is_visible():
                        continue

                    title = (
                        heading
                        .inner_text()
                        .strip()
                    )

                    if not title:
                        continue

                    # ------------------------------------------------
                    # FIND CLOSEST LINK
                    # ------------------------------------------------

                    href = heading.evaluate(
                        """
                        (element) => {
                            const link = element.closest("a");

                            if (!link) {
                                return null;
                            }

                            return link.href;
                        }
                        """
                    )

                    if not href:
                        print(
                            f"[Browser] No link found for: {title}"
                        )
                        continue

                    # ------------------------------------------------
                    # VALIDATE URL
                    # ------------------------------------------------

                    if not href:
                        print(
                            f"[Browser] No link found for: "
                            f"{title}"
                        )
                        continue

                    if not (
                        href.startswith("http://")
                        or
                        href.startswith("https://")
                    ):
                        continue

                    # ------------------------------------------------
                    # IGNORE GOOGLE INTERNAL LINKS
                    # ------------------------------------------------

                    if (
                        "google.com/search" in href
                        or
                        "accounts.google.com" in href
                    ):
                        continue

                    # ------------------------------------------------
                    # REMOVE DUPLICATES
                    # ------------------------------------------------

                    if any(
                        item["url"] == href
                        for item in results
                    ):
                        continue

                    # ------------------------------------------------
                    # SAVE RESULT
                    # ------------------------------------------------

                    resolved_url = resolve_google_url(
                        page,
                        href
                    )

                    if not resolved_url:
                        continue

                    results.append({
                        "position": len(results) + 1,
                        "title": title,
                        "url": resolved_url
                    })

                    print(
                        f"[Browser] Result "
                        f"{len(results)}: "
                        f"{title} -> {href}"
                    )

                    # Maximum 10 results
                    if len(results) >= 10:
                        break

                except Exception as error:

                    print(
                        f"[Browser] Could not read "
                        f"result {i + 1}: {error}"
                    )

        except Exception as error:

            print(
                f"[Browser] Result extraction failed: "
                f"{error}"
            )

        # --------------------------------------------------------
        # FINAL RESULT REPORT
        # --------------------------------------------------------

        print(
            f"[Browser] Google results found: "
            f"{len(results)}"
        )

        for result in results:

            print(
                f"  {result['position']}. "
                f"{result['title']} -> "
                f"{result['url']}"
            )

        # --------------------------------------------------------
        # RETURN STRUCTURED RESULT
        # --------------------------------------------------------

        return {
            "success": True,
            "engine": "google",
            "query": query,
            "url": page.url,
            "results": results,
            "count": len(results),
            "message": (
                f"Found {len(results)} Google "
                f"search result(s) for: {query}"
            )
        }

    except Exception as error:

        return {
            "success": False,
            "error": (
                f"Google search failed: {error}"
            )
        }


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

        result = navigate_page(page, url)

        if not result["success"]:
            return (
                f"Could not open {name}: "
                f"{result['error']}"
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
    global _context
    global _page
    global _pages
    global _active_page_index

    try:
        print("[Browser] Closing browser...")

        if _context is not None:
            try:
                _context.close()
            except Exception:
                pass

        if _browser is not None:
            try:
                _browser.close()
            except Exception:
                pass

        if _playwright is not None:
            try:
                _playwright.stop()
            except Exception:
                pass

        _playwright = None
        _browser = None
        _context = None
        _page = None
        _pages = []
        _active_page_index = 0

        return {
            "success": True,
            "message": "Browser closed."
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }

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
