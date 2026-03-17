"""
core/voice.py
=============
pyttsx3 MUST live on ONE permanent thread forever.
Every speak() call sends text to that thread via a queue.
speak()       = blocking  (waits for audio to finish)
speak_async() = non-blocking
"""

import threading
import queue
import pyttsx3

_q     = queue.Queue()
_done  = threading.Event()
_ready = threading.Event()


def _tts_worker():
    """Single permanent thread that owns pyttsx3."""
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate",   148)
        engine.setProperty("volume", 0.95)

        voices = engine.getProperty("voices")
        chosen = None
        for v in voices:
            if any(x in v.name.lower() for x in ["zira","hazel","helena"]):
                chosen = v.id
                break
        if chosen is None and len(voices) > 1:
            chosen = voices[1].id
        if chosen:
            engine.setProperty("voice", chosen)
            print(f"[TTS] voice: {chosen}")

        _ready.set()
        print("[TTS] ready.")

        while True:
            text = _q.get()        # wait for next item
            if text is None:       # poison pill
                break
            _done.clear()
            try:
                if len(text) > 280:
                    text = text[:280] + ". And more."
                print(f"[TTS] >> {text[:70]}")
                engine.say(text)
                engine.runAndWait()
                print("[TTS] done.")
            except Exception as exc:
                print(f"[TTS] error: {exc}")
                try:
                    engine = pyttsx3.init()
                except Exception:
                    pass
            finally:
                _done.set()        # ALWAYS signal done

    except Exception as exc:
        print(f"[TTS] worker init error: {exc}")
        _ready.set()
        _done.set()


# start exactly once on import
threading.Thread(target=_tts_worker, daemon=True, name="TTS").start()
_ready.wait(timeout=8)


def speak(text: str):
    """Blocking — returns only after audio finishes. Thread-safe."""
    if not text or not text.strip():
        return
    _done.clear()
    _q.put(text)
    _done.wait()


def speak_async(text: str):
    """Non-blocking — returns immediately."""
    if not text or not text.strip():
        return
    _q.put(text)
