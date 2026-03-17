"""
integrations/file_search.py
-----------------------------
Search files on the PC by name.
Searches Desktop, Documents, Downloads, and C:\\ drive.
"""

import os
import glob
import subprocess


QUICK_DIRS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Music"),
    os.path.expanduser("~/Videos"),
    os.path.expanduser("~/Pictures"),
    "C:/CYRUS",
]


def search_files(query: str, max_results: int = 8) -> str:
    """Search for files matching query in common directories first, then C:\\"""
    query   = query.lower().strip()
    found   = []

    # quick search in common dirs
    for directory in QUICK_DIRS:
        if not os.path.exists(directory):
            continue
        for root, dirs, files in os.walk(directory):
            # skip hidden and system folders
            dirs[:] = [d for d in dirs
                       if not d.startswith(".") and d not in
                       {"node_modules", "__pycache__", "AppData"}]
            for f in files:
                if query in f.lower():
                    found.append(os.path.join(root, f))
                    if len(found) >= max_results:
                        break
            if len(found) >= max_results:
                break

    # if not enough, try C:\\ (slower)
    if len(found) < 3:
        try:
            result = subprocess.run(
                ["where", "/r", "C:\\", f"*{query}*"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if line and line not in found:
                    found.append(line)
                    if len(found) >= max_results:
                        break
        except:
            pass

    if not found:
        return f"No files found matching '{query}'."

    names = [os.path.basename(f) for f in found[:max_results]]
    reply = f"Found {len(found)} file(s) matching '{query}': " + \
            ", ".join(names[:5])
    if len(found) > 5:
        reply += f" and {len(found)-5} more."
    return reply


def open_file(query: str) -> str:
    """Find and open the first matching file."""
    query = query.lower().strip()

    for directory in QUICK_DIRS:
        if not os.path.exists(directory):
            continue
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if query in f.lower():
                    full = os.path.join(root, f)
                    try:
                        os.startfile(full)
                        return f"Opening {f}."
                    except Exception as e:
                        return f"Found {f} but could not open it: {e}"

    return f"Could not find any file matching '{query}'."


def open_folder(path: str) -> str:
    """Open a folder in Explorer."""
    if os.path.exists(path):
        os.startfile(path)
        return f"Opened folder: {path}"
    # try common folders by name
    shortcuts = {
        "desktop":   os.path.expanduser("~/Desktop"),
        "documents": os.path.expanduser("~/Documents"),
        "downloads": os.path.expanduser("~/Downloads"),
        "pictures":  os.path.expanduser("~/Pictures"),
        "music":     os.path.expanduser("~/Music"),
        "videos":    os.path.expanduser("~/Videos"),
        "cyrus":     "C:/CYRUS",
    }
    p = path.lower().strip()
    if p in shortcuts:
        os.startfile(shortcuts[p])
        return f"Opened {path} folder."
    return f"Folder '{path}' not found."
