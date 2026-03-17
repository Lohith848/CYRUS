"""
setup.py
--------
CYRUS One-Click Setup Script.
Run this FIRST before launching CYRUS.
  >> python setup.py
"""

import os
import sys
import subprocess
import json


BASE_DIR = r"C:\CYRUS"

PACKAGES = [
    "vosk",
    "pyaudio",
    "pyttsx3",
    "PyQt5",
    "requests",
    "psutil",
    "pillow",
    "pyautogui",
    "keyboard",
    "pystray",
    "google-auth",
    "google-auth-oauthlib",
    "google-api-python-client",
    "notion-client",
    "selenium",
    "webdriver-manager",
    "pycaw",
    "comtypes",
]

DIRS = [
    r"C:\CYRUS\logs",
    r"C:\CYRUS\config",
    r"C:\CYRUS\memory",
    r"C:\CYRUS\models",
    r"C:\CYRUS\memory\chrome_profile",
]

VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
VOSK_MODEL_PATH = r"C:\CYRUS\models\vosk-model-en-us-0.22"


def section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


def step(msg):
    print(f"\n  >> {msg}")


def ok(msg):
    print(f"  ✓  {msg}")


def warn(msg):
    print(f"  ⚠  {msg}")


def create_directories():
    section("Creating Directories")
    for d in DIRS:
        os.makedirs(d, exist_ok=True)
        ok(f"Created: {d}")


def install_packages():
    section("Installing Python Packages")
    print("  This may take a few minutes...\n")
    failed = []
    for pkg in PACKAGES:
        step(f"Installing {pkg}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            ok(f"{pkg} installed.")
        else:
            warn(f"{pkg} FAILED: {result.stderr.strip()[:80]}")
            failed.append(pkg)

    if failed:
        print(f"\n  ⚠  Failed packages: {', '.join(failed)}")
        print("     Try installing them manually: pip install <package>")
    else:
        print("\n  ✓  All packages installed!")


def check_ollama():
    section("Checking Ollama")
    import requests
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            ok(f"Ollama running. Models: {', '.join(models) if models else 'none'}")
            if not any("llama" in m for m in models):
                warn("llama3 not found. Pull it with:  ollama pull llama3")
            return True
        else:
            warn("Ollama responded but with error.")
    except:
        warn("Ollama not running. Start it with:  ollama serve")
        warn("Then pull a model:                  ollama pull llama3")
    return False


def check_vosk_model():
    section("Checking Vosk Voice Model")
    if os.path.exists(VOSK_MODEL_PATH):
        ok(f"Model found at {VOSK_MODEL_PATH}")
        return True
    warn(f"Vosk model NOT found at {VOSK_MODEL_PATH}")
    print("""
  To install the Vosk model:
  1. Go to: https://alphacephei.com/vosk/models
  2. Download: vosk-model-en-us-0.22.zip  (1.8 GB)
  3. Extract it to: C:\\CYRUS\\models\\
     So the path becomes: C:\\CYRUS\\models\\vosk-model-en-us-0.22\\

  For a smaller model (faster, less accurate):
  Download: vosk-model-small-en-us-0.15  (only 40 MB)
  Then update config/settings.json:  "vosk_model_path": "C:/CYRUS/models/vosk-model-small-en-us-0.15"
    """)
    return False


def create_default_settings():
    section("Creating Config Files")
    settings_path = r"C:\CYRUS\config\settings.json"

    if os.path.exists(settings_path):
        ok("settings.json already exists — skipping.")
        return

    settings = {
        "wake_word": "hey cyrus",
        "ollama_model": "llama3",
        "ollama_url": "http://localhost:11434",
        "vosk_model_path": "C:/CYRUS/models/vosk-model-en-us-0.22",
        "user_name": "sir",
        "voice": {
            "rate": 175,
            "volume": 0.9,
            "preferred_voice": "david"
        },
        "gmail": {
            "credentials_file": "C:/CYRUS/config/gmail_credentials.json",
            "token_file": "C:/CYRUS/config/gmail_token.json"
        },
        "notion": {
            "api_key": "YOUR_NOTION_API_KEY_HERE"
        },
        "apps": {
            "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "vscode": "code",
            "notepad": "notepad.exe"
        }
    }
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
    ok(f"Created: {settings_path}")


def check_python_version():
    section("Checking Python Version")
    v = sys.version_info
    if v.major == 3 and v.minor >= 9:
        ok(f"Python {v.major}.{v.minor}.{v.micro} — OK")
    else:
        warn(f"Python {v.major}.{v.minor} — Recommend Python 3.9 or newer.")


def summary():
    section("SETUP COMPLETE — NEXT STEPS")
    print("""
  1. VOSK MODEL (voice recognition):
     Download from: https://alphacephei.com/vosk/models
     File: vosk-model-en-us-0.22.zip
     Extract to: C:\\CYRUS\\models\\

  2. OLLAMA (AI brain):
     Install from: https://ollama.com
     Then run:  ollama pull llama3

  3. GMAIL INTEGRATION (optional):
     - Go to: https://console.cloud.google.com
     - Create project > Enable Gmail API
     - Download credentials.json
     - Save as: C:\\CYRUS\\config\\gmail_credentials.json
     - First run will ask you to log in

  4. NOTION INTEGRATION (optional):
     - Go to: https://www.notion.so/my-integrations
     - Create integration > Copy API key
     - Paste in: C:\\CYRUS\\config\\settings.json

  5. START CYRUS:
     cd C:\\CYRUS
     python launch.py          ← Full HUD (recommended)
     python cyrus.py           ← Background voice-only mode

  6. ADD TO WINDOWS STARTUP (optional):
     python boot\\add_to_startup.py
    """)


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  CYRUS AI Assistant — Setup")
    print("="*55)

    check_python_version()
    create_directories()
    install_packages()
    create_default_settings()
    check_vosk_model()
    check_ollama()
    summary()
