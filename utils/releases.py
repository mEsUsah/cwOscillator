import threading
import webbrowser
import requests
from tkinter import messagebox

APP_VERSION = "v1.0.0"
_RELEASES_URL = "https://api.github.com/repos/mEsUsah/cwOscillator/releases/latest"
_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def _do_check():
    try:
        response = requests.get(_RELEASES_URL, headers=_HEADERS, timeout=5)
        data = response.json()
        latest = data.get("name") or data.get("tag_name")
        if latest and latest != APP_VERSION:
            message = f"CW Oscillator {latest} is released!\n\nDo you want to open the download page?"
            if messagebox.askyesno("New version", message, icon="question", default="yes"):
                webbrowser.open(data["html_url"])
    except Exception:
        pass  # silently ignore network errors


def check_updates():
    threading.Thread(target=_do_check, daemon=True).start()
