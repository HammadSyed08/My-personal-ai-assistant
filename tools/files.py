from pathlib import Path
import shutil
import os

from config import CURRENT_WORKING_DIR


# ============================================================
# PATH HANDLING
# ============================================================

def resolve_path(path_text):

    """
    Convert natural Windows locations and relative paths
    into a Windows Path object.
    """

    if not path_text:
        return Path(CURRENT_WORKING_DIR) / path

    path_text = str(path_text).strip()

    # --------------------------------------------------------
    # Expand environment variables
    # --------------------------------------------------------

    path_text = os.path.expandvars(path_text)
    path_text = os.path.expanduser(path_text)

    # --------------------------------------------------------
    # Special Windows folders
    # --------------------------------------------------------

    special_locations = {

        "desktop": Path.home() / "Desktop",

        "my desktop": Path.home() / "Desktop",

        "downloads": Path.home() / "Downloads",

        "my downloads": Path.home() / "Downloads",

        "documents": Path.home() / "Documents",

        "my documents": Path.home() / "Documents",

        "pictures": Path.home() / "Pictures",

        "my pictures": Path.home() / "Pictures",

        "videos": Path.home() / "Videos",

        "my videos": Path.home() / "Videos",

        "music": Path.home() / "Music",

        "my music": Path.home() / "Music",
    }

    normalized = path_text.lower()

    if normalized in special_locations:

        return special_locations[normalized]

    # --------------------------------------------------------
    # Absolute Windows path
    # --------------------------------------------------------

    path = Path(path_text)

    if path.is_absolute():

        return path

    # --------------------------------------------------------
    # Relative path
    # --------------------------------------------------------

    return Path(CURRENT_WORKING_DIR) / path


# ============================================================
# Trace Current Directory
# ============================================================

def get_current_directory():

    try:

        path = Path(CURRENT_WORKING_DIR)

        return f"Current working directory: {path}"

    except Exception as error:

        return f"Could not determine current directory: {error}"


def search_files(search_term, location=""):

    search_term = search_term.strip().lower()

    if not search_term:

        return "Please provide something to search for."

    base_path = resolve_path(location)

    try:

        if not base_path.exists():

            return f"Search location doesn't exist: {base_path}"

        results = []

        for item in base_path.rglob("*"):

            if search_term in item.name.lower():

                if item.is_dir():

                    results.append(
                        f"[FOLDER] {item}"
                    )

                else:

                    results.append(
                        f"[FILE] {item}"
                    )

            # Prevent enormous responses
            if len(results) >= 50:

                break

        if not results:

            return (
                f"No files or folders matching "
                f"'{search_term}' were found."
            )

        return "\n".join(results)

    except Exception as error:

        return f"Search failed: {error}"

    
# ============================================================
# CREATE FOLDER
# ============================================================

def create_folder(path_text):

    path = resolve_path(path_text)

    try:

        if path.exists():

            return f"The folder already exists: {path}"

        path.mkdir(
            parents=True,
            exist_ok=False
        )

        return f"Folder created successfully: {path}"

    except Exception as error:

        return f"Could not create folder: {error}"


# ============================================================
# OPEN FOLDER
# ============================================================

def open_folder(path_text):

    path = resolve_path(path_text)

    try:

        if not path.exists():

            return f"I couldn't find this folder: {path}"

        if not path.is_dir():

            return f"This path is not a folder: {path}"

        os.startfile(str(path))

        return f"Opened folder: {path}"

    except Exception as error:

        return f"Could not open folder: {error}"


# ============================================================
# CLOSE FOLDER
# ============================================================

def close_folder(path_text):

    path = resolve_path(path_text)

    try:

        if not path.exists():
            return f"I couldn't find this folder: {path}"

        if not path.is_dir():
            return f"This path is not a folder: {path}"

        import win32gui
        import win32com.client

        shell = win32com.client.Dispatch("Shell.Application")

        target_path = str(path.resolve()).lower().rstrip("\\")

        for window in shell.Windows():

            try:

                current_path = window.Document.Folder.Self.Path

                if not current_path:
                    continue

                current_path = (
                    str(current_path)
                    .lower()
                    .rstrip("\\")
                )

                if current_path == target_path:

                    hwnd = window.HWND

                    win32gui.PostMessage(
                        hwnd,
                        0x0010,  # WM_CLOSE
                        0,
                        0
                    )

                    return f"Closed folder: {path}"

            except Exception:
                continue

        return f"I couldn't find an open Explorer window for: {path}"

    except Exception as error:

        return f"Could not close folder: {error}"

# ============================================================
# LIST DIRECTORY
# ============================================================

def list_directory(path_text=""):

    path = resolve_path(path_text)

    try:

        if not path.exists():

            return f"Path doesn't exist: {path}"

        if not path.is_dir():

            return f"This path is not a folder: {path}"

        items = list(path.iterdir())

        if not items:

            return f"The folder is empty: {path}"

        folders = []
        files = []

        for item in items:

            if item.is_dir():

                folders.append(
                    f"[FOLDER] {item.name}"
                )

            else:

                files.append(
                    f"[FILE] {item.name}"
                )

        result = []

        result.append(
            f"Contents of {path}:"
        )

        result.extend(
            sorted(folders)
        )

        result.extend(
            sorted(files)
        )

        return "\n".join(result)

    except Exception as error:

        return f"Could not read folder: {error}"


# ============================================================
# CREATE FILE
# ============================================================

def create_file(path_text, content=""):

    path = resolve_path(path_text)

    try:

        if path.exists():

            return f"The file already exists: {path}"

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        path.write_text(
            content,
            encoding="utf-8"
        )

        return f"File created successfully: {path}"

    except Exception as error:

        return f"Could not create file: {error}"


# ============================================================
# READ FILE
# ============================================================

def read_file(path_text):

    path = resolve_path(path_text)

    try:

        if not path.exists():

            return f"I couldn't find the file: {path}"

        if not path.is_file():

            return f"This path is not a file: {path}"

        content = path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        if not content:

            return f"The file is empty: {path}"

        return content[:10000]

    except Exception as error:

        return f"Could not read file: {error}"


# ============================================================
# RENAME
# ============================================================

def rename_item(old_path_text, new_name):

    old_path = resolve_path(old_path_text)

    try:

        if not old_path.exists():

            return f"I couldn't find: {old_path}"

        new_path = old_path.parent / new_name

        if new_path.exists():

            return (
                f"An item with that name already exists: "
                f"{new_path}"
            )

        old_path.rename(new_path)

        return (
            f"Renamed successfully:\n"
            f"{old_path.name} → {new_path.name}"
        )

    except Exception as error:

        return f"Rename failed: {error}"


# ============================================================
# COPY
# ============================================================

def copy_item(source_text, destination_text):

    source = resolve_path(source_text)
    destination = resolve_path(destination_text)

    try:

        if not source.exists():

            return f"I couldn't find: {source}"

        if source.is_dir():

            shutil.copytree(
                source,
                destination
            )

        else:

            # If destination is a folder,
            # copy the file inside it.
            if destination.exists() and destination.is_dir():

                destination = (
                    destination / source.name
                )

            shutil.copy2(
                source,
                destination
            )

        return (
            f"Copied successfully:\n"
            f"{source}\n→\n{destination}"
        )

    except Exception as error:

        return f"Copy failed: {error}"


# ============================================================
# MOVE
# ============================================================

def move_item(source_text, destination_text):

    source = resolve_path(source_text)
    destination = resolve_path(destination_text)

    try:

        if not source.exists():

            return f"I couldn't find: {source}"

        if destination.exists() and destination.is_dir():

            destination = (
                destination / source.name
            )

        shutil.move(
            str(source),
            str(destination)
        )

        return (
            f"Moved successfully:\n"
            f"{source}\n→\n{destination}"
        )

    except Exception as error:

        return f"Move failed: {error}"


# ============================================================
# DELETE FILE
# ============================================================

def delete_file(path_text):

    path = resolve_path(path_text)

    try:

        if not path.exists():

            return f"I couldn't find: {path}"

        if not path.is_file():

            return f"This is not a file: {path}"

        path.unlink()

        return f"File deleted: {path}"

    except Exception as error:

        return f"Delete failed: {error}"


# ============================================================
# DELETE FOLDER
# ============================================================

def delete_folder(path_text):

    path = resolve_path(path_text)

    try:

        if not path.exists():

            return f"I couldn't find: {path}"

        if not path.is_dir():

            return f"This is not a folder: {path}"

        shutil.rmtree(path)

        return f"Folder deleted: {path}"

    except Exception as error:

        return f"Folder deletion failed: {error}"