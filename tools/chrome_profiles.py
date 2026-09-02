import json
import os
import subprocess


# ============================================================
# CHROME USER DATA
# ============================================================

CHROME_USER_DATA = os.path.expandvars(
    r"%LOCALAPPDATA%\Google\Chrome\User Data"
)


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


# ============================================================
# OPEN CHROME PROFILE
# ============================================================

def open_chrome_profile(profile_name):
    """
    Open Google Chrome using a specific Chrome profile name.
    """

    if not profile_name:
        return {
            "success": False,
            "error": "Chrome profile name was not provided."
        }

    profile_name = profile_name.strip().lower()

    # Get all Chrome profiles
    result = list_chrome_profiles()

    if not result.get("success"):
        return result

    profiles = result.get("profiles", [])

    # Find requested profile
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
            "error": (
                f"Chrome profile '{profile_name}' was not found.",
            ),
            "available_profiles": available
        }

    chrome_path = get_chrome_path()

    if not chrome_path:
        return {
            "success": False,
            "error": "Google Chrome executable was not found."
        }

    directory = selected_profile.get("directory")

    if not directory:
        return {
            "success": False,
            "error": (
                f"Profile '{profile_name}' does not have "
                f"a valid Chrome directory."
            )
        }

    try:

        subprocess.Popen([
            chrome_path,
            f"--profile-directory={directory}"
        ])

        return {
            "success": True,
            "profile": selected_profile.get("name"),
            "directory": directory,
            "email": selected_profile.get("email", ""),
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