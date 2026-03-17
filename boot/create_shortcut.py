"""
boot/create_shortcut.py
------------------------
Creates:
  1. Desktop shortcut → double-click to launch CYRUS
  2. Windows startup entry → CYRUS auto-starts on boot

Run once:  py -3.10 boot/create_shortcut.py
"""

import os, sys, subprocess

CYRUS_DIR   = r"C:\CYRUS"
LAUNCH_PY   = r"C:\CYRUS\launch.py"
PYTHON_310  = r"C:\Users\Public\python310"   # fallback; auto-detected below

# ── find py -3.10 ────────────────────────────────────────────────
def find_python310():
    for candidate in [
        r"C:\Users\Lohith G\AppData\Local\Programs\Python\Python310\pythonw.exe",
        r"C:\Python310\pythonw.exe",
        r"C:\Program Files\Python310\pythonw.exe",
    ]:
        if os.path.exists(candidate):
            return candidate
    # fallback — use py launcher
    return "py -3.10 -m pythonw"


def create_desktop_shortcut():
    python = find_python310()
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut = os.path.join(desktop, "CYRUS.lnk")

    script = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{python}"
oLink.Arguments = "{LAUNCH_PY}"
oLink.WorkingDirectory = "{CYRUS_DIR}"
oLink.Description = "CYRUS AI Assistant"
oLink.IconLocation = "{python}"
oLink.Save
"""
    vbs = os.path.join(CYRUS_DIR, "_make_shortcut.vbs")
    with open(vbs, "w") as f:
        f.write(script)
    subprocess.run(["cscript", "//nologo", vbs], check=True)
    os.remove(vbs)
    print(f"[CYRUS] Desktop shortcut created: {shortcut}")


def add_to_startup():
    python = find_python310()
    startup = os.path.expanduser(
        r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\CYRUS.bat"
    )
    bat = f'@echo off\nstart /min "" "{python}" "{LAUNCH_PY}"\n'
    with open(startup, "w") as f:
        f.write(bat)
    print(f"[CYRUS] Added to Windows startup: {startup}")


if __name__ == "__main__":
    try:
        create_desktop_shortcut()
    except Exception as e:
        print(f"Shortcut error: {e}")
    try:
        add_to_startup()
    except Exception as e:
        print(f"Startup error: {e}")
    print("\nDone! CYRUS will now start automatically on boot.")
    print("Desktop shortcut created — double-click to open.")
