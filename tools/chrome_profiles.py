import json
import os
import subprocess


# ============================================================
# CHROME USER DATA
# ============================================================

CHROME_USER_DATA = os.path.expandvars(
    r"%LOCALAPPDATA%\Google\Chrome\User Data"
)

_current_profile = None

# Remote debugging ports for Chrome profiles
_profile_debug_ports = {}

_next_debug_port = 9222


# ============================================================
# CHROME PATH
# ============================================================

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


def get_chrome_path():
    """
    Find installed Google Chrome.
    """

    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path

    return None


# ============================================================
# GET CHROME PROFILES
# ============================================================

def get_chrome_profiles():

    local_state_path = os.path.join(
        CHROME_USER_DATA,
        "Local State"
    )

    if not os.path.exists(local_state_path):
        return {
            "success": False,
            "error": "Chrome Local State file was not found."
        }

    try:

        with open(
            local_state_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        profile_info = data.get(
            "profile",
            {}
        )

        profiles = profile_info.get(
            "info_cache",
            {}
        )

        result = []

        for directory, information in profiles.items():

            name = information.get(
                "name",
                directory
            )

            email = information.get(
                "user_name",
                ""
            )

            result.append(
                {
                    "name": name,
                    "directory": directory,
                    "email": email
                }
            )

        return {
            "success": True,
            "profiles": result
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# FIND CHROME PROFILE
# ============================================================

def find_chrome_profile(profile_name):

    result = get_chrome_profiles()

    if not result.get("success"):
        return result

    profiles = result.get(
        "profiles",
        []
    )

    search = profile_name.lower().strip()

    # Exact match first
    for profile in profiles:

        if profile["name"].lower() == search:

            return {
                "success": True,
                "profile": profile
            }

    # Partial match
    matches = []

    for profile in profiles:

        if search in profile["name"].lower():

            matches.append(profile)

    if len(matches) == 1:

        return {
            "success": True,
            "profile": matches[0]
        }

    if len(matches) > 1:

        return {
            "success": False,
            "multiple": True,
            "matches": matches,
            "error": "Multiple Chrome profiles matched."
        }

    return {
        "success": False,
        "error": f"Chrome profile '{profile_name}' was not found."
    }


def get_profile_debug_port(directory):
    global _profile_debug_ports
    global _next_debug_port

    if directory in _profile_debug_ports:
        return _profile_debug_ports[directory]

    port = _next_debug_port

    _profile_debug_ports[directory] = port
    _next_debug_port += 1

    return port


# ============================================================
# OPEN CHROME PROFILE
# ============================================================

def open_chrome_profile(profile_name, open_new_tab=False, website=None):
    """
    Open Google Chrome using a specific Chrome profile.

    Chrome is launched with remote debugging enabled so that
    Playwright can connect to the real Chrome instance.
    """

    global _current_profile

    if not profile_name:
        return {
            "success": False,
            "error": "Chrome profile name was not provided."
        }

    profile_name = profile_name.strip().lower()

    # --------------------------------------------------------
    # GET ALL CHROME PROFILES
    # --------------------------------------------------------

    result = list_chrome_profiles()

    if not result.get("success"):
        return result

    profiles = result.get("profiles", [])

    # --------------------------------------------------------
    # FIND REQUESTED PROFILE
    # --------------------------------------------------------

    selected_profile = None

    for profile in profiles:

        name = profile.get("name", "").strip().lower()

        if name == profile_name:
            selected_profile = profile
            break

    if selected_profile is None:

        available = [
            profile.get("name", "")
            for profile in profiles
        ]

        return {
            "success": False,
            "error": f"Chrome profile '{profile_name}' was not found.",
            "available_profiles": available
        }

    # --------------------------------------------------------
    # GET CHROME PATH
    # --------------------------------------------------------

    chrome_path = get_chrome_path()

    if not chrome_path:
        return {
            "success": False,
            "error": "Google Chrome executable was not found."
        }

    # --------------------------------------------------------
    # GET PROFILE DIRECTORY
    # --------------------------------------------------------

    directory = selected_profile.get("directory")

    if not directory:
        return {
            "success": False,
            "error": (
                f"Profile '{profile_name}' does not have "
                f"a valid Chrome directory."
            )
        }

    # --------------------------------------------------------
    # GET DEBUGGING PORT
    # --------------------------------------------------------

    debug_port = get_profile_debug_port(directory)

    # Save selected profile
    _current_profile = selected_profile

    # --------------------------------------------------------
    # BUILD CHROME COMMAND
    # --------------------------------------------------------

    chrome_command = [
        chrome_path,

        f"--profile-directory={directory}",

        f"--remote-debugging-port={debug_port}",

        "--remote-allow-origins=http://localhost",

    ]

    # --------------------------------------------------------
    # WEBSITE
    # --------------------------------------------------------

    if website:

        website = website.strip()

        if not website.startswith(("http://", "https://")):
            website = "https://" + website

        chrome_command.append(website)

    # --------------------------------------------------------
    # OPEN CHROME
    # --------------------------------------------------------

    try:

        print(
            f"[Chrome] Opening profile: "
            f"{selected_profile.get('name')}"
        )

        print(
            f"[Chrome] Debugging port: {debug_port}"
        )

        subprocess.Popen(chrome_command)

        return {
            "success": True,
            "profile": selected_profile.get("name"),
            "directory": directory,
            "debug_port": debug_port,
            "website": website,
            "open_new_tab": open_new_tab,
            "message": (
                f"Opened Chrome profile "
                f"'{selected_profile.get('name')}'."
            )
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }

def list_chrome_profiles():

    result = get_chrome_profiles()

    if not result.get("success"):
        return result

    profiles = result.get(
        "profiles",
        []
    )

    return {
        "success": True,
        "profiles": profiles
    }


# ============================================================
# GET CURRENT CHROME PROFILE
# ============================================================

def get_current_chrome_profile():
    global _current_profile

    if _current_profile is None:
        return {
            "success": False,
            "error": "No Chrome profile is currently selected."
        }

    return {
        "success": True,
        "profile": _current_profile.get("name"),
        "directory": _current_profile.get("directory"),
        "email": _current_profile.get("email", "")
    }