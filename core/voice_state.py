"""core/voice_state.py — global mic on/off flag"""
_mic = True

def mic_enabled() -> bool:
    return _mic

def set_mic(v: bool):
    global _mic
    _mic = v
    print(f"[MIC] {'ON' if v else 'OFF'}")
