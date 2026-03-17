"""
voice/listener.py — nova wake word
Say "nova" → wake → say command → command runs → HUD auto-hides
Listener just handles wake/command routing. HUD handles its own hiding.
"""
import vosk, pyaudio, json, threading, os, re

_STRIP = re.compile(
    r"^(the|a|an|uh|um|er|hmm|oh|so|hey|hi|ok|okay|nova|"
    r"please|can you|could you|would you)\s*[,.]?\s*",
    re.IGNORECASE,
)

def _clean(text):
    prev = None
    while prev != text:
        prev = text
        text = _STRIP.sub("", text).strip()
    return text

WAKE = {"nova", "no va", "noval", "novah", "over", "mova"}
EXIT = {"exit", "close", "bye", "goodbye", "stop", "sleep", "quit"}

def _is_wake(t): return t in WAKE or bool(set(t.split()) & WAKE)
def _is_exit(t): return t in EXIT or bool(set(t.split()) & EXIT)


class VoiceListener:
    RATE = 16000; CHUNK = 4096

    def __init__(self, model_path, wake_words=None):
        self.model_path  = model_path
        self._on_command = None
        self._on_wake    = None
        self._running    = False
        self._active     = False   # waiting for command
        self._busy       = False   # command running
        self._model      = None
        self._load()

    def _load(self):
        if not os.path.exists(self.model_path):
            print(f"[Voice] Model NOT found: {self.model_path}"); return
        try:
            vosk.SetLogLevel(-1)
            self._model = vosk.Model(self.model_path)
            print("[Voice] Model loaded OK.")
        except Exception as e:
            print(f"[Voice] Load error: {e}")

    def start(self, on_command, on_wake=None, on_sleep=None):
        if not self._model:
            print("[Voice] No model."); return
        self._on_command = on_command
        self._on_wake    = on_wake
        # on_sleep ignored — HUD hides itself after command
        self._running    = True
        threading.Thread(target=self._loop, daemon=True,
                         name="CyrusVoice").start()
        print("[Voice] Sleeping — say 'Nova' to wake.")

    def stop(self): self._running = False
    def activate(self): self._active = True

    def _loop(self):
        try:
            audio  = pyaudio.PyAudio()
            rec    = vosk.KaldiRecognizer(self._model, self.RATE)
            stream = audio.open(format=pyaudio.paInt16, channels=1,
                                rate=self.RATE, input=True,
                                frames_per_buffer=self.CHUNK)
            stream.start_stream()
            print("[Voice] Mic open OK.")
        except Exception as e:
            print(f"[Voice] Mic error: {e}"); return

        while self._running:
            try:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
            except Exception: continue

            if not rec.AcceptWaveform(data): continue

            raw = json.loads(rec.Result()).get("text","").strip()
            if not raw: continue

            # skip while speaking or busy
            try:
                from core.voice_state import mic_enabled
                if not mic_enabled(): continue
            except Exception: pass

            if self._busy: continue

            text = raw.lower().strip()
            print(f"[Voice] heard: '{text}'  active={self._active}")

            # ── SLEEPING ───────────────────────────────────────────
            if not self._active:
                if _is_wake(text):
                    self._active = True
                    print("[Voice] *** WAKE ***")
                    if self._on_wake:
                        threading.Thread(target=self._on_wake,
                                         daemon=True).start()
                continue

            # ── ACTIVE ─────────────────────────────────────────────
            if _is_exit(text):
                self._active = False
                print("[Voice] manual exit")
                continue

            cmd = _clean(text)
            if not cmd or len(cmd) < 3: continue

            # execute command, then go back to sleep
            self._active = False
            self._busy   = True
            print(f"[Voice] command: '{cmd}'")

            def _exec(c):
                try:
                    self._on_command(c)
                    # wait for command_handler to finish speaking
                    import time; time.sleep(0.5)
                finally:
                    self._busy = False
                    print("[Voice] ready for next wake word.")

            threading.Thread(target=_exec, args=(cmd,),
                             daemon=True).start()

        stream.stop_stream(); stream.close(); audio.terminate()
