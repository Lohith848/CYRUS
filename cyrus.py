"""
cyrus.py
--------
CYRUS AI Assistant — Main entry point (background/headless mode).
Runs voice processing without the HUD. Use launch.py for the HUD.
"""

import os
import sys
import time
import json
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

LOG_FILE = os.path.join(BASE_DIR, "logs", "cyrus.log")
SETTINGS_FILE = os.path.join(BASE_DIR, "config", "settings.json")


def log(msg: str):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass


def load_settings():
    try:
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        log("settings.json not found — using defaults.")
        return {}
    except Exception as e:
        log(f"Settings error: {e}")
        return {}


def main():
    log("=" * 60)
    log("CYRUS AI Assistant starting (background mode)...")

    settings = load_settings()

    # Router
    router = None
    try:
        from core.command_router import CommandRouter
        router = CommandRouter()
        log("Command router ready.")
    except Exception as e:
        log(f"Router init failed: {e}")

    # Speaker
    speaker = None
    try:
        from voice.speaker import Speaker
        v = settings.get("voice", {})
        speaker = Speaker(
            rate=v.get("rate", 175),
            volume=v.get("volume", 0.9),
            preferred_voice=v.get("preferred_voice", "david")
        )
        log("Speaker ready.")
    except Exception as e:
        log(f"Speaker init failed: {e}")

    # Voice Listener
    listener = None
    try:
        from voice.listener import VoiceListener

        def on_command(text: str):
            log(f"Command: {text}")
            if router:
                response = router.route(text)
                log(f"Response: {response}")
                if response == "SHUTDOWN":
                    log("Shutdown command received.")
                    os._exit(0)
                if speaker:
                    speaker.speak(response)
            else:
                log("No router available.")

        listener = VoiceListener(
            model_path=settings.get("vosk_model_path", "C:/CYRUS/models/vosk-model-en-us-0.22"),
            wake_word=settings.get("wake_word", "hey cyrus")
        )
        listener.start(on_command)
        log("Voice listener started.")
    except Exception as e:
        log(f"Voice listener failed: {e}")

    if speaker:
        speaker.speak("CYRUS online. Ready for your commands, sir.")

    log("CYRUS running. Say 'Hey Cyrus' to activate.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("CYRUS shutdown via keyboard.")
        if listener:
            listener.stop()


if __name__ == "__main__":
    main()
