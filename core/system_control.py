"""
core/system_control.py
Full system control — NO visible CMD windows.
"""
import os, subprocess, webbrowser, psutil, time, re, winreg
from datetime import datetime

# Windows flag to hide CMD popup
_SI = subprocess.STARTUPINFO()
_SI.dwFlags |= subprocess.STARTF_USESHOWWINDOW
_SI.wShowWindow = subprocess.SW_HIDE

def _run(cmd, timeout=5):
    """Run command silently, return stdout."""
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, startupinfo=_SI
        )
        return r.stdout.strip()
    except:
        return ""

# ── app discovery ─────────────────────────────────────────────────
_CACHE = None

def _apps():
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    _CACHE = {}

    # Registry App Paths
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for kp in [r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                   r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"]:
            try:
                key = winreg.OpenKey(hive, kp)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        name = winreg.EnumKey(key, i)
                        sub  = winreg.OpenKey(key, name)
                        path, _ = winreg.QueryValueEx(sub, "")
                        _CACHE[name.lower().replace(".exe","")] = path
                    except: pass
            except: pass

    # Start Menu shortcuts
    for sm in [os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
               r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"]:
        for root, _, files in os.walk(sm):
            for f in files:
                if f.endswith(".lnk"):
                    _CACHE[f[:-4].lower()] = os.path.join(root, f)

    # manual reliable overrides
    _CACHE.update({
        "chrome":     r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "brave":      r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        "firefox":    r"C:\Program Files\Mozilla Firefox\firefox.exe",
        "edge":       r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "notepad":    "notepad.exe",
        "calculator": "calc.exe",
        "explorer":   "explorer.exe",
        "task manager":"taskmgr.exe",
        "cmd":        "cmd.exe",
        "powershell": "powershell.exe",
        "paint":      "mspaint.exe",
        "vscode":     "code",
        "code":       "code",
        "spotify":    os.path.expanduser(r"~\AppData\Roaming\Spotify\Spotify.exe"),
        "whatsapp":   os.path.expanduser(r"~\AppData\Local\WhatsApp\WhatsApp.exe"),
        "telegram":   os.path.expanduser(r"~\AppData\Roaming\Telegram Desktop\Telegram.exe"),
        "discord":    os.path.expanduser(r"~\AppData\Local\Discord\app-*\Discord.exe"),
        "steam":      r"C:\Program Files (x86)\Steam\steam.exe",
        "vlc":        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    })
    return _CACHE

WEB = {
    "whatsapp":  "https://web.whatsapp.com",
    "instagram": "https://www.instagram.com",
    "youtube":   "https://www.youtube.com",
    "gmail":     "https://mail.google.com",
    "telegram":  "https://web.telegram.org",
    "notion":    "https://www.notion.so",
    "github":    "https://github.com",
    "twitter":   "https://twitter.com",
    "linkedin":  "https://linkedin.com",
    "netflix":   "https://netflix.com",
    "reddit":    "https://reddit.com",
    "maps":      "https://maps.google.com",
    "drive":     "https://drive.google.com",
    "calendar":  "https://calendar.google.com",
    "spotify":   "https://open.spotify.com",
}

FOLDERS = {
    "desktop":   os.path.expanduser("~/Desktop"),
    "documents": os.path.expanduser("~/Documents"),
    "downloads": os.path.expanduser("~/Downloads"),
    "pictures":  os.path.expanduser("~/Pictures"),
    "music":     os.path.expanduser("~/Music"),
    "videos":    os.path.expanduser("~/Videos"),
    "cyrus":     "C:/CYRUS",
}


class SystemControl:

    def open(self, name: str) -> str:
        n = name.lower().strip()

        # folder shortcut
        if n in FOLDERS:
            try:
                os.startfile(FOLDERS[n])
                return f"Opened {name} folder."
            except Exception as e:
                return f"Could not open {name}: {e}"

        # web shortcut
        if n in WEB:
            webbrowser.open(WEB[n])
            return f"Opening {name.capitalize()} in browser."

        apps = _apps()

        # exact match
        if n in apps:
            return self._launch(apps[n], name)

        # partial match
        for k, v in apps.items():
            if n in k or k in n:
                return self._launch(v, k)

        # safe exe fallback
        SAFE = {"notepad.exe","calc.exe","mspaint.exe","explorer.exe",
                "taskmgr.exe","cmd.exe","powershell.exe","code","wordpad.exe"}
        if n in SAFE or n.endswith(".exe"):
            try:
                subprocess.Popen(n, startupinfo=_SI, shell=False)
                return f"Opening {n}."
            except: pass

        return f"Could not find '{name}'. Make sure it is installed."

    def _launch(self, path: str, name: str) -> str:
        try:
            subprocess.Popen(path, startupinfo=_SI, shell=True)
            return f"Opening {name.title()}."
        except Exception as e:
            return f"Failed to open {name}: {e}"

    def close(self, name: str) -> str:
        killed = []
        for p in psutil.process_iter(["name","pid"]):
            if name.lower() in p.info["name"].lower():
                try:
                    p.terminate()
                    killed.append(p.info["name"])
                except: pass
        return (f"Closed {', '.join(set(killed))}." if killed
                else f"'{name}' is not running.")

    def google(self, q: str) -> str:
        webbrowser.open(f"https://google.com/search?q={q.replace(' ','+')}")
        return f"Searching Google for {q}."

    def youtube(self, q: str) -> str:
        webbrowser.open(f"https://youtube.com/results?search_query={q.replace(' ','+')}")
        return f"Searching YouTube for {q}."

    def spotify_search(self, q: str) -> str:
        webbrowser.open(f"https://open.spotify.com/search/{q.replace(' ','%20')}")
        return f"Searching Spotify for {q}."

    def open_url(self, url: str) -> str:
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opening {url}."

    def system_info(self) -> str:
        try:
            cpu   = psutil.cpu_percent(interval=0.5)
            ram   = psutil.virtual_memory()
            disk  = psutil.disk_usage("C:/")
            bat   = psutil.sensors_battery()
            bat_s = (f"{bat.percent:.0f} percent "
                     f"{'charging' if bat.power_plugged else 'discharging'}"
                     if bat else "no battery")

            # GPU — silent, no CMD popup
            gpu_s = ""
            try:
                out = _run(["nvidia-smi",
                            "--query-gpu=utilization.gpu,memory.used,memory.total",
                            "--format=csv,noheader,nounits"], timeout=3)
                if out:
                    u, used, total = [x.strip() for x in out.split(",")]
                    gpu_s = f". GPU {u} percent, {used} of {total} megabytes used"
            except: pass

            return (
                f"CPU is at {cpu} percent. "
                f"RAM is {ram.percent} percent used, "
                f"{ram.used//1024**3} of {ram.total//1024**3} gigabytes. "
                f"Disk C is {disk.percent} percent used. "
                f"Battery {bat_s}{gpu_s}."
            )
        except Exception as e:
            return f"System info error: {e}"

    def time_now(self) -> str:
        return f"It is {datetime.now().strftime('%I:%M %p')}."

    def date_now(self) -> str:
        return f"Today is {datetime.now().strftime('%A, %B %d %Y')}."

    def set_volume(self, level: int) -> str:
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            dev = AudioUtilities.GetSpeakers()
            ifc = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            cast(ifc, POINTER(IAudioEndpointVolume)).SetMasterVolumeLevelScalar(
                max(0, min(100, level)) / 100.0, None)
            return f"Volume set to {level} percent."
        except Exception as e:
            return f"Volume error: {e}"

    def mute(self) -> str:
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            dev = AudioUtilities.GetSpeakers()
            ifc = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            cast(ifc, POINTER(IAudioEndpointVolume)).SetMute(1, None)
            return "Muted."
        except: return "Could not mute."

    def unmute(self) -> str:
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            dev = AudioUtilities.GetSpeakers()
            ifc = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            cast(ifc, POINTER(IAudioEndpointVolume)).SetMute(0, None)
            return "Unmuted."
        except: return "Could not unmute."

    def shutdown(self, delay=10) -> str:
        subprocess.Popen(f"shutdown /s /t {delay}",
                         shell=True, startupinfo=_SI)
        return f"Shutting down in {delay} seconds."

    def restart(self, delay=5) -> str:
        subprocess.Popen(f"shutdown /r /t {delay}",
                         shell=True, startupinfo=_SI)
        return f"Restarting in {delay} seconds."

    def sleep(self) -> str:
        subprocess.Popen(
            "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
            shell=True, startupinfo=_SI)
        return "Going to sleep."

    def lock(self) -> str:
        subprocess.Popen(
            "rundll32.exe user32.dll,LockWorkStation",
            shell=True, startupinfo=_SI)
        return "Workstation locked."

    def cancel_shutdown(self) -> str:
        subprocess.Popen("shutdown /a", shell=True, startupinfo=_SI)
        return "Shutdown cancelled."

    def screenshot(self) -> str:
        try:
            import pyautogui
            path = f"C:/CYRUS/memory/shot_{int(time.time())}.png"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            pyautogui.screenshot(path)
            return "Screenshot saved."
        except Exception as e:
            return f"Screenshot failed: {e}"

    def whatsapp_web(self) -> str:
        webbrowser.open("https://web.whatsapp.com")
        return "Opened WhatsApp Web."

    def telegram_web(self) -> str:
        webbrowser.open("https://web.telegram.org")
        return "Opened Telegram Web."
