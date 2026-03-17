"""
boot/add_to_startup.py
-----------------------
Run this ONCE to add CYRUS to Windows startup.
It creates a shortcut in the Windows Startup folder.
"""

import os
import sys
import shutil


def add_to_startup():
    startup_folder = os.path.expanduser(
        r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    bat_src = r"C:\CYRUS\boot\startup.bat"
    bat_dst = os.path.join(startup_folder, "CYRUS.bat")

    try:
        shutil.copy2(bat_src, bat_dst)
        print(f"[CYRUS] Added to Windows startup: {bat_dst}")
        print("[CYRUS] CYRUS will now start automatically on login.")
    except Exception as e:
        print(f"[CYRUS] Failed to add to startup: {e}")


def remove_from_startup():
    startup_folder = os.path.expanduser(
        r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    bat_dst = os.path.join(startup_folder, "CYRUS.bat")
    if os.path.exists(bat_dst):
        os.remove(bat_dst)
        print("[CYRUS] Removed from Windows startup.")
    else:
        print("[CYRUS] CYRUS was not in startup.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        remove_from_startup()
    else:
        add_to_startup()
