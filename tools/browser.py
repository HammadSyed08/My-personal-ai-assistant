from playwright.sync_api import sync_playwright
from urllib.parse import quote_plus

import urllib.request
import urllib.error
import threading
import os
import subprocess
import time
import urllib.request
import json
import re
import queue
import functools
from concurrent.futures import Future

# ============================================================
# BROWSER EXECUTOR THREAD
# ------------------------------------------------------------
# Playwright's sync API is bound to the thread that created it.
# Every browser call MUST run on this single thread.
# ============================================================

_executor_queue = queue.Queue()
_executor_thread = None
_executor_thread_lock = threading.Lock()
_executor_local = threading.local()


def _executor_loop():
    _executor_local.is_browser_thread = True
    while True:
        item = _executor_queue.get()
        if item is None:
            return
        func, args, kwargs, future = item
        try:
            result = func(*args, **kwargs)
            if not future.cancelled():
                future.set_result(result)
        except BaseException as exc:
            if not future.cancelled():
                future.set_exception(exc)


def _ensure_executor():
    global _executor_thread
    with _executor_thread_lock:
        if _executor_thread is None or not _executor_thread.is_alive():
            _executor_thread = threading.Thread(
                target=_executor_loop,
                name="HammuBrowserThread",
                daemon=True,
            )
            _executor_thread.start()


def run_in_browser_thread(func):
    """Decorator: force `func` to execute on the single browser thread."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Already on the browser thread? Call directly to avoid deadlock.
        if getattr(_executor_local, "is_browser_thread", False):
            return func(*args, **kwargs)

        _ensure_executor()
        future = Future()
        _executor_queue.put((func, args, kwargs, future))
        return future.result()

    return wrapper

# ============================================================
# PERSISTENT BROWSER ENGINE
# ============================================================

_playwright = None
_browser = None
_context = None
_page = None

_pages = []
_active_page_index = 0
_active_profile_dir = None

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

def get_chrome_profile_directory(profile_name):
    """
    Find Chrome's internal profile directory from its friendly profile name.

    Example:
        "Work" -> "Profile 28"
        "Fear is" -> "Profile 30"
        "letfocused" -> "Default"
    """

    chrome_user_data = os.path.expandvars(
        r"%LOCALAPPDATA%\Google\Chrome\User Data"
    )

    local_state_path = os.path.join(
        chrome_user_data,
        "Local State"
    )

    try:
        with open(local_state_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        profiles = data.get("profile", {}).get("info_cache", {})

        profile_name_normalized = profile_name.strip().lower()

        for directory, profile_info in profiles.items():
            name = profile_info.get("name", "")

            if name.strip().lower() == profile_name_normalized:
                print(
                    f"[HAMMU Chrome] Profile '{profile_name}' "
                    f"-> '{directory}'"
                )
                return directory

        print(
            f"[HAMMU Chrome] Profile '{profile_name}' not found."
        )
        return None

    except Exception as e:
        print(f"[HAMMU Chrome] Could not read Chrome profiles: {e}")
        return None

def start_hammu_chrome(profile_name="Default"):
    """
    Start an isolated persistent Chrome profile for HAMMU.

    Each friendly profile name gets its own HAMMU data directory.
    This keeps HAMMU separate from the user's normal Chrome profiles
    and allows Chrome CDP to work reliably on modern Chrome versions.

    Examples:
        start_hammu_chrome("Work")
        start_hammu_chrome("Fear is")
        start_hammu_chrome("Syed")
    """
    global _active_profile_dir

    print(f"[HAMMU Chrome] Requested profile: {profile_name}")

    if not profile_name or not profile_name.strip():
        print("[HAMMU Chrome] Profile name cannot be empty.")
        return False

    chrome_path = get_chrome_executable()

    if not chrome_path:
        print("[HAMMU Chrome] Chrome executable not found.")
        return False

    # Create one persistent, isolated data directory per HAMMU profile.
    # Example:
    #   hammu_chrome/Work
    #   hammu_chrome/Fear is
    #
    # This is intentionally NOT the user's normal Chrome User Data folder.
    safe_profile_name = re.sub(r'[^A-Za-z0-9._ -]+', '_', profile_name.strip())
    safe_profile_name = safe_profile_name.strip(" .")

    if not safe_profile_name:
        print("[HAMMU Chrome] Invalid profile name.")
        return False

    profile_data_dir = os.path.join(
        HAMMU_CHROME_DATA,
        safe_profile_name
    )

    os.makedirs(profile_data_dir, exist_ok=True)

    _active_profile_dir = profile_data_dir

    # If CDP is already running, do not start another Chrome instance
    # on the same debugging port.
    if chrome_cdp_available():
        print(
            f"[HAMMU Chrome] Chrome is already running on "
            f"port {HAMMU_CHROME_PORT}."
        )
        return True

    chrome_command = [
        chrome_path,
        f"--remote-debugging-port={HAMMU_CHROME_PORT}",
        f"--user-data-dir={profile_data_dir}",
        "--remote-allow-origins=http://localhost",
        "--no-first-run",
        "--no-default-browser-check",
        "--new-window",
        "about:blank",
    ]

    print(
        f"[HAMMU Chrome] Starting isolated profile: "
        f"{profile_name}"
    )
    print(
        f"[HAMMU Chrome] Data directory: "
        f"{profile_data_dir}"
    )

    try:
        subprocess.Popen(
            chrome_command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception as e:
        print(f"[HAMMU Chrome] Failed to start Chrome: {e}")
        return False

    print("[HAMMU Chrome] Waiting for Chrome...")

    for _ in range(30):
        if chrome_cdp_available():
            print("[HAMMU Chrome] Chrome started successfully.")
            return True

        time.sleep(0.5)

    print("[HAMMU Chrome] Chrome did not become available.")
    return False

# ============================================================
# START BROWSER
# ============================================================


@run_in_browser_thread
def start_browser():
    print(f"[Browser Thread] start_browser: {threading.get_ident()}")

    global _playwright
    global _browser
    global _context
    global _page
    global _pages
    global _active_page_index
    global _active_profile_dir

    # ---------------------------------------------------------
    # Reuse existing Playwright browser
    # ---------------------------------------------------------

    if (
        _playwright is not None
        and _context is not None
        and _page is not None
    ):
        try:
            if not _page.is_closed():
                print("[Browser] Existing Playwright browser is ready.")
                return _page
        except Exception:
            pass

    # ---------------------------------------------------------
    # Clean old Playwright objects
    # ---------------------------------------------------------

    _playwright = None
    _browser = None
    _context = None
    _page = None
    _pages = []
    _active_page_index = 0

    try:
        print("[Browser] Starting Playwright...")

        _playwright = sync_playwright().start()

        print("[Browser] Launching HAMMU Chrome...")

        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]

        chrome_path = None

        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break

        if chrome_path is None:
            print("[Browser] Chrome executable not found.")
            return None

        print(f"[Browser] Chrome executable: {chrome_path}")

        # Make sure HAMMU Chrome is running before connecting.
        if not chrome_cdp_available():
            print("[Browser] HAMMU Chrome is not running. Starting it...")

            if not start_hammu_chrome("Work"):
                print("[Browser] Failed to start HAMMU Chrome.")
                return None
            
        print(f"[Browser] Connecting to Chrome on port {HAMMU_CHROME_PORT}...")

        _browser = _playwright.chromium.connect_over_cdp(
            f"http://127.0.0.1:{HAMMU_CHROME_PORT}"
        )

        if not _browser.contexts:
            print("[Browser] No browser context found.")
            return None

        _context = _browser.contexts[0]

        _pages = [
            page
            for page in _context.pages
            if not page.is_closed()
        ]

        if not _pages:
            print("[Browser] No tabs found. Creating one...")
            _page = _context.new_page()
            _pages = [_page]
        else:
            _page = _pages[0]

        _active_page_index = 0

        try:
            _page.bring_to_front()
        except Exception:
            pass

        print(
            f"[Browser] HAMMU Chrome ready with "
            f"{len(_pages)} tab(s)."
        )

        return _page

    except Exception as error:
        print(
            f"[Browser Error] Could not start browser: {error}"
        )

        try:
            if _context is not None:
                _context.close()
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

@run_in_browser_thread
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
        if _context is None:
            print("[Browser] Browser context is unavailable. Restarting...")
            close_browser()
            return start_browser()
    except Exception:
        print("[Browser] Browser context check failed. Restarting...")
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
@run_in_browser_thread
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
        new_page = _create_tab_via_cdp(url or "about:blank", timeout=15.0)

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

@run_in_browser_thread
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

@run_in_browser_thread
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


@run_in_browser_thread
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


@run_in_browser_thread
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

def _get_any_live_page():
    """
    Return a page that is definitely alive.

    Never trust the _page global — it can be stale after a
    temporary tab is closed by the redirect resolver.
    """
    global _pages, _active_page_index, _page

    if _context is None:
        raise RuntimeError("Browser context is not ready.")

    _pages = [p for p in _context.pages if not p.is_closed()]

    if not _pages:
        raise RuntimeError("No live pages available.")

    # Prefer the current _page if it still responds.
    if _page is not None:
        try:
            if not _page.is_closed():
                _ = _page.url          # smoke test
                return _page
        except Exception:
            pass

    if _active_page_index >= len(_pages):
        _active_page_index = len(_pages) - 1
    if _active_page_index < 0:
        _active_page_index = 0

    _page = _pages[_active_page_index]
    return _page

def _create_tab_via_cdp(url="about:blank", timeout=20.0, make_active=True):
    """
    Open a new Chrome tab via raw CDP Target.createTarget.

    Playwright's BrowserContext.new_page() over connect_over_cdp()
    segfaults on the default context, so we use the CDP primitive.

    make_active=False → the new tab is NOT promoted to _page.
                        Use this for throw-away pages.
    """
    global _pages, _active_page_index, _page

    if _context is None:
        raise RuntimeError("Browser context is not ready.")

    anchor = _get_any_live_page()

    before = {id(p) for p in _context.pages}

    cdp = _context.new_cdp_session(anchor)
    try:
        cdp.send("Target.createTarget", {"url": url or "about:blank"})
    finally:
        try:
            cdp.detach()
        except Exception:
            pass

    deadline = time.time() + timeout
    new_page = None
    while time.time() < deadline:
        for p in _context.pages:
            if id(p) not in before:
                try:
                    if not p.is_closed():
                        new_page = p
                        break
                except Exception:
                    continue
        if new_page is not None:
            break
        time.sleep(0.05)

    if new_page is None:
        raise RuntimeError("New tab did not appear after Target.createTarget.")

    if make_active:
        _pages = [p for p in _context.pages if not p.is_closed()]
        try:
            _active_page_index = _pages.index(new_page)
        except ValueError:
            _active_page_index = len(_pages) - 1
        _page = new_page
        try:
            new_page.bring_to_front()
        except Exception:
            pass

    return new_page

@run_in_browser_thread
def open_url(url):
    ...
    print(f"[Browser] Opening URL: {url}")

    try:
       new_page = _create_tab_via_cdp(url, timeout=15.0)
    except Exception as error:
        print(f"[Browser Error] Could not open URL: {error}")
        return {"success": False, "error": str(error)}

    print("[Browser Debug] New tab created via CDP.")
    print(f"[Browser Debug] Active HAMMU tab: {_active_page_index + 1}")

    return {
        "success": True,
        "message": "Website opened.",
        "url": new_page.url,
    }
# ============================================================
# GOOGLE SEARCH
# ============================================================


@run_in_browser_thread
def resolve_google_url(page, google_url):
    global _pages, _active_page_index, _page

    if not google_url or "/goto?" not in google_url:
        return google_url

    print(f"[Browser] Resolving Google redirect:\n    From: {google_url}")

    # ---------- 1. HTTP attempt ----------
    try:
        req = urllib.request.Request(
            google_url,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE      # tolerate SSL-inspection proxies

        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            final_url = resp.geturl()

        if final_url and "/goto?" not in final_url:
            print(f"[Browser] Google redirect resolved (HTTP):\n    To:   {final_url}")
            return final_url
    except Exception as e:
        print(f"[Browser] HTTP redirect resolve failed: {e}")

    # ---------- 2. Browser attempt in a NON-active temp tab ----------
    try:
        temp_page = _create_tab_via_cdp(
            google_url, timeout=10.0, make_active=False
        )
        try:
            temp_page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass

        final_url = temp_page.url

        try:
            temp_page.close(run_before_unload=False)
        except Exception:
            pass

        # Refresh state now that the temp tab is gone.
        _pages = [p for p in _context.pages if not p.is_closed()]
        if _active_page_index >= len(_pages):
            _active_page_index = max(0, len(_pages) - 1)
        if _pages:
            _page = _pages[_active_page_index]

        if final_url and "/goto?" not in final_url:
            print(f"[Browser] Google redirect resolved (Browser):\n    To:   {final_url}")
            return final_url
    except Exception as e:
        print(f"[Browser] Browser redirect resolve failed: {e}")

    return google_url


@run_in_browser_thread
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
                        f"{title} -> {resolved_url}"
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
@run_in_browser_thread
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


@run_in_browser_thread
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

@run_in_browser_thread
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

@run_in_browser_thread
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

@run_in_browser_thread
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

@run_in_browser_thread
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

@run_in_browser_thread
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

@run_in_browser_thread
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

@run_in_browser_thread
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
