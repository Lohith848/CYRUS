"""
core/command_handler.py
=======================
Single entry point for every command.
try/finally guarantees mic is ALWAYS re-enabled even if speak() crashes.
"""

import sys
import traceback
import threading

sys.path.insert(0, "C:/CYRUS")

_router = None


def _get_router():
    global _router
    if _router is None:
        from core.command_router import CommandRouter
        _router = CommandRouter()
    return _router


def handle_command(text: str) -> str:
    from core.voice       import speak
    from core.voice_state import set_mic

    print(f"[CMD] '{text}'")

    # --- route command ---
    try:
        reply = _get_router().route(text)
    except Exception:
        traceback.print_exc()
        reply = "Sorry sir, something went wrong."

    if not reply:
        reply = "Done."

    # --- SHUTDOWN special case ---
    if reply == "SHUTDOWN":
        set_mic(False)
        speak("Goodbye sir.")
        set_mic(True)
        def _quit():
            import time
            time.sleep(1.5)
            try:
                from PySide6.QtWidgets import QApplication
                QApplication.quit()
            except Exception:
                pass
        threading.Thread(target=_quit, daemon=True).start()
        return reply

    # --- speak reply, ALWAYS re-enable mic in finally ---
    set_mic(False)
    try:
        speak(reply)           # blocking
    except Exception as exc:
        print(f"[CMD] speak failed: {exc}")
    finally:
        set_mic(True)          # ALWAYS runs, even if speak() threw
        print("[CMD] mic ON.")

    return reply
