"""
core/command_router.py  —  CYRUS command router
All routes in priority order. Tested patterns only.
"""

import re, datetime, os, webbrowser
from core.system_control   import SystemControl
from core.brain            import Brain
from memory.memory_manager import MemoryManager

_sys   = SystemControl()
_brain = Brain()
_mem   = MemoryManager()

# folder shortcuts
FOLDERS = {
    "desktop":   os.path.expanduser("~/Desktop"),
    "documents": os.path.expanduser("~/Documents"),
    "downloads": os.path.expanduser("~/Downloads"),
    "pictures":  os.path.expanduser("~/Pictures"),
    "music":     os.path.expanduser("~/Music"),
    "videos":    os.path.expanduser("~/Videos"),
    "cyrus":     "C:/CYRUS",
}

FILLER = re.compile(
    r"^(the|a|an|uh|um|er|oh|hmm|so|hey|hi|ok|okay|please|"
    r"can you|could you|would you|i want to|i need you to|"
    r"cyrus|serious|sirius|siri)\s+",
    re.IGNORECASE
)

def _clean(t: str) -> str:
    prev = None
    while prev != t:
        prev = t
        t = FILLER.sub("", t).strip()
    return t


class CommandRouter:
    def __init__(self):
        self.sys   = _sys
        self.brain = _brain
        self.mem   = _mem

    def route(self, raw: str) -> str:
        t = _clean(raw.lower().strip())
        if not t or len(t) < 2:
            return "Yes sir, I am listening."

        # ── greetings ────────────────────────────────────────────
        if re.match(r"^(hello|hi|hey|good morning|good afternoon|good evening|what'?s up)$", t):
            h = datetime.datetime.now().hour
            g = "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"
            return f"{g} sir. CYRUS is ready."

        # ── time / date ──────────────────────────────────────────
        if re.search(r"\btime\b", t) and not re.search(r"\bwhat\s+time.*meeting\b", t):
            return self.sys.time_now()
        if re.search(r"\b(date|today|what day)\b", t):
            return self.sys.date_now()

        # ── weather ──────────────────────────────────────────────
        if re.search(r"\b(weather|temperature|forecast|rain|sunny|humidity|hot|cold)\b", t):
            from integrations.weather import get_weather, get_forecast
            m = re.search(r"\b(?:in|at|for)\s+([a-z][a-z\s]{1,20}?)(?:\s*$|\s+today|\s+now)", t)
            city = m.group(1).strip() if m else ""
            if "forecast" in t:
                return get_forecast(city)
            return get_weather(city)

        # ── system info ──────────────────────────────────────────
        if re.search(r"\b(cpu|ram|memory|disk|battery|gpu|system info|system status|pc status|health)\b", t):
            return self.sys.system_info()

        # ── screenshot ───────────────────────────────────────────
        if re.search(r"\bscreenshot\b", t):
            return self.sys.screenshot()

        # ── volume ───────────────────────────────────────────────
        m = re.search(r"volume\s+(?:to\s+)?(\d+)", t)
        if m: return self.sys.set_volume(int(m.group(1)))
        if re.search(r"\bmute\b", t) and "unmute" not in t: return self.sys.mute()
        if re.search(r"\bunmute\b", t): return self.sys.unmute()
        if re.search(r"volume.*(up|high|louder|increase|raise)", t): return self.sys.set_volume(80)
        if re.search(r"volume.*(down|low|quiet|decrease|lower)", t): return self.sys.set_volume(30)

        # ── power ────────────────────────────────────────────────
        if re.search(r"\bshut\s*down\b|\bturn\s*off\b|\bpower\s*off\b", t):
            m2 = re.search(r"in\s+(\d+)", t)
            return self.sys.shutdown(int(m2.group(1)) if m2 else 10)
        if re.search(r"\b(restart|reboot)\b", t): return self.sys.restart()
        if re.search(r"\b(sleep|hibernate)\b", t): return self.sys.sleep()
        if re.search(r"\block\s*(screen|pc|computer|laptop)?\b", t): return self.sys.lock()
        if re.search(r"\bcancel\s*(shutdown|restart)\b", t): return self.sys.cancel_shutdown()

        # ── open folder shortcuts ─────────────────────────────────
        for name, path in FOLDERS.items():
            if re.search(rf"\b(open|show|go to)\s+(?:my\s+)?{name}\b", t):
                try:
                    os.startfile(path)
                    return f"Opened {name} folder."
                except Exception as e:
                    return f"Could not open {name}: {e}"

        # ── file search ───────────────────────────────────────────
        m = re.search(r"\b(find|search for|look for)\s+(?:file\s+)?(?:called\s+)?(.+?)(?:\s+file)?$", t)
        if m:
            from integrations.file_search import search_files
            return search_files(m.group(2).strip())

        # ── open file ─────────────────────────────────────────────
        m = re.search(r"\bopen\s+file\s+(.+)", t)
        if m:
            from integrations.file_search import open_file
            return open_file(m.group(1).strip())

        # ── gmail ────────────────────────────────────────────────
        if re.search(r"\b(read|check|show|any|my)\b.*\b(email|mail|gmail|inbox)\b", t):
            from integrations.gmail_integration import read_emails
            return read_emails()
        m = re.search(
            r"\b(?:send|compose|write)\b.*?(?:email|mail)\b.*?\bto\b\s+(\S+)\b.*?\babout\b\s+(.+)", t)
        if m:
            from integrations.gmail_integration import send_email
            return send_email(m.group(1), m.group(2), m.group(2))

        # ── whatsapp ─────────────────────────────────────────────
        m = re.search(
            r"(?:send|message|whatsapp)\s+(.+?)\s+(?:on\s+whatsapp\s+)?(?:saying|message|that)\s+(.+)", t)
        if m:
            from integrations.messaging import send_whatsapp
            return send_whatsapp(m.group(1).strip(), m.group(2).strip())
        if re.search(r"\bwhatsapp\b", t):
            webbrowser.open("https://web.whatsapp.com")
            return "Opened WhatsApp Web."

        # ── telegram ─────────────────────────────────────────────
        # "send telegram to John saying hello"
        # "telegram John hello"
        # "message John on telegram saying hi"
        m = re.search(
            r"(?:send\s+)?telegram\s+(?:to\s+)?(.+?)\s+"
            r"(?:saying|message|that|:)\s+(.+)", t)
        if m:
            from integrations.telegram_bot import send_message
            return send_message(m.group(1).strip(), m.group(2).strip())

        m = re.search(
            r"(?:send|message)\s+(.+?)\s+on\s+telegram\s+"
            r"(?:saying|message|that|:)\s+(.+)", t)
        if m:
            from integrations.telegram_bot import send_message
            return send_message(m.group(1).strip(), m.group(2).strip())

        if re.search(r"(telegram contacts|my telegram contacts)", t):
            from integrations.telegram_bot import list_contacts
            return list_contacts()

        if re.search(r"(telegram messages|check telegram|read telegram)", t):
            from integrations.telegram_bot import get_updates
            return get_updates()

        if re.search(r"\btelegram\b", t):
            webbrowser.open("https://web.telegram.org")
            return "Opened Telegram Web."

        # ── notion ───────────────────────────────────────────────
        m = re.search(r"(?:create|add|new)\s+(?:a\s+)?(?:notion\s+)?note\s+(?:about\s+|for\s+)?(.+)", t)
        if m:
            from integrations.notion_integration import create_note
            return create_note(m.group(1).strip())
        if re.search(r"\bnotion\b", t):
            webbrowser.open("https://notion.so")
            return "Opened Notion."

        # ── memory: remember ─────────────────────────────────────
        m = re.search(r"\bremember\s+(?:that\s+)?(?:my\s+)?(.+?)\s+is\s+(.+)", t)
        if m:
            return self.mem.remember(m.group(1).strip(), m.group(2).strip())
        m = re.search(r"\bremember\s+(?:that\s+)?(.+)", t)
        if m:
            return self.mem.add_reminder(m.group(1).strip())

        # ── memory: note ─────────────────────────────────────────
        m = re.search(r"\b(?:note|write down|save)\s+(?:that\s+)?(.+)", t)
        if m:
            return self.mem.add_note(m.group(1).strip())

        # ── memory: recall ────────────────────────────────────────
        if re.search(r"\bwhat\s+(?:is|are|was)\s+(?:my\s+)?(.+)", t):
            m = re.search(r"\bwhat\s+(?:is|are|was)\s+(?:my\s+)?(.+)", t)
            if m:
                key = m.group(1).strip().rstrip("?")
                result = self.mem.recall(key)
                if "don't have" not in result:
                    return result
                # else fall through to brain

        # ── show notes / reminders ────────────────────────────────
        if re.search(r"\b(my notes|show notes|list notes)\b", t):
            return self.mem.list_notes()
        if re.search(r"\b(my reminders|show reminders|list reminders)\b", t):
            return self.mem.list_reminders()
        if re.search(r"\b(what do you remember|what do you know about me)\b", t):
            return self.mem.list_facts()
        if re.search(r"\bforget\s+(.+)", t):
            m = re.search(r"\bforget\s+(.+)", t)
            return self.mem.forget(m.group(1).strip()) if m else "Forget what?"

        # ── youtube search ────────────────────────────────────────
        m = re.search(r"(?:play|search|find)\s+(.+?)\s+on\s+youtube$", t)
        if m: return self.sys.youtube(m.group(1))
        m = re.search(r"youtube\s+(.+)", t)
        if m: return self.sys.youtube(m.group(1))

        # ── spotify ───────────────────────────────────────────────
        m = re.search(r"(?:play|search)\s+(.+?)\s+on\s+spotify$", t)
        if m: return self.sys.spotify_search(m.group(1))
        m = re.search(r"spotify\s+(.+)", t)
        if m: return self.sys.spotify_search(m.group(1))

        # ── open app / website ────────────────────────────────────
        m = re.search(r"^(?:open|launch|start|run)\s+(.+)", t)
        if m: return self.sys.open(m.group(1).strip())

        m = re.search(r"^(?:go to|visit)\s+(\S+)", t)
        if m: return self.sys.open_url(m.group(1))

        # ── close ─────────────────────────────────────────────────
        m = re.search(r"^(?:close|kill|quit|stop)\s+(.+)", t)
        if m: return self.sys.close(m.group(1).strip())

        # ── google search ─────────────────────────────────────────
        m = re.search(r"(?:search|google|look up)\s+(.+)", t)
        if m: return self.sys.google(m.group(1))

        # ── memory clear ──────────────────────────────────────────
        if re.search(r"\b(clear|reset)\s+(memory|history|conversation)\b", t):
            return self.brain.clear()

        # ── exit ──────────────────────────────────────────────────
        if re.match(r"^(bye|goodbye|exit|quit|close cyrus|sleep)$", t):
            return "SHUTDOWN"

        # ── fallback → Ollama ─────────────────────────────────────
        return self.brain.ask(raw)
