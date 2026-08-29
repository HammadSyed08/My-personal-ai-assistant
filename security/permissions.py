from pathlib import Path


# ============================================================
# HAMMU AI SECURITY POLICY
# ============================================================

# Only E: is available to the AI.
ALLOWED_DRIVES = {
    "E:",
    "C:",
    # "F:",
}

# These drives are permanently protected.
PROTECTED_DRIVES = {
    # "C:",
    "D:",
    "F:"
}


# ============================================================
# GET DRIVE
# ============================================================

def get_drive(path):

    try:
        path = Path(path)

        # Windows Path.drive
        drive = path.drive.upper()

        return drive

    except Exception:
        return ""


# ============================================================
# CHECK DRIVE
# ============================================================

def is_drive_allowed(path):

    drive = get_drive(path)

    if not drive:
        return False

    return drive in ALLOWED_DRIVES


# ============================================================
# CHECK PROTECTED DRIVE
# ============================================================

def is_drive_protected(path):

    drive = get_drive(path)

    return drive in PROTECTED_DRIVES


# ============================================================
# AUTHORIZE PATH
# ============================================================

def authorize_path(path):

    path = Path(path)

    drive = get_drive(path)

    if not drive:

        return False, (
            "Security blocked this operation because "
            "the path does not specify an allowed drive."
        )

    if drive in PROTECTED_DRIVES:

        return False, (
            f"ACCESS DENIED: {drive}\\ is protected. "
            f"Hammu AI cannot modify this drive."
        )

    if drive not in ALLOWED_DRIVES:

        return False, (
            f"ACCESS DENIED: {drive}\\ is not an allowed "
            f"Hammu AI workspace."
        )

    return True, "Access granted."


# ============================================================
# REQUIRE CONFIRMATION
# ============================================================

def requires_confirmation(action):

    dangerous_actions = {

        "delete_file",
        "delete_folder",
        "move_item",
        "overwrite_file",
        "execute_command",
        "run_powershell",
        "shutdown",
        "restart",
    }

    return action in dangerous_actions


# ============================================================
# USER CONFIRMATION
# ============================================================

def ask_confirmation(action, target):

    print()
    print("=" * 60)
    print("⚠️  SECURITY CONFIRMATION REQUIRED")
    print("=" * 60)

    print(f"Action : {action}")
    print(f"Target : {target}")

    print()
    print("This operation can modify or remove data.")

    answer = input(
        "Do you want to continue? (yes/no): "
    ).strip().lower()

    print("=" * 60)

    return answer in {
        "yes",
        "y"
    }