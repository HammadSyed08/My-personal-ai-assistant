import webbrowser
from urllib.parse import quote_plus


# ============================================================
# OPEN URL
# ============================================================

def open_url(url):

    if not url:
        return "No URL was provided."

    url = url.strip()

    # Automatically add https://
    if not url.startswith(
        ("http://", "https://")
    ):
        url = "https://" + url

    try:

        webbrowser.open(url)

        return f"Opened: {url}"

    except Exception as error:

        return f"Could not open URL: {error}"


# ============================================================
# GOOGLE SEARCH
# ============================================================

def google_search(query):

    if not query:
        return "Search query was not provided."

    encoded_query = quote_plus(query)

    url = (
        "https://www.google.com/search?q="
        + encoded_query
    )

    try:

        webbrowser.open(url)

        return f"Searching Google for: {query}"

    except Exception as error:

        return f"Google search failed: {error}"


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def youtube_search(query):

    if not query:
        return "YouTube search query was not provided."

    encoded_query = quote_plus(query)

    url = (
        "https://www.youtube.com/results?search_query="
        + encoded_query
    )

    try:

        webbrowser.open(url)

        return f"Searching YouTube for: {query}"

    except Exception as error:

        return f"YouTube search failed: {error}"


# ============================================================
# OPEN WEBSITE
# ============================================================

WEBSITES = {

    "google":
        "https://www.google.com",

    "youtube":
        "https://www.youtube.com",

    "github":
        "https://github.com",

    "chatgpt":
        "https://chatgpt.com",

    "gmail":
        "https://mail.google.com",

    "facebook":
        "https://www.facebook.com",

    "linkedin":
        "https://www.linkedin.com",

    "whatsapp":
        "https://web.whatsapp.com",

    "stackoverflow":
        "https://stackoverflow.com",

    "reddit":
        "https://www.reddit.com",
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

        webbrowser.open(url)

        return f"Opened {name}."

    except Exception as error:

        return f"Could not open {name}: {error}"