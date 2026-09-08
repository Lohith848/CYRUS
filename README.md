# CYRUS — Personal AI Assistant

> Voice-controlled intelligence for your laptop. Say **"Nova"** to wake it up.

**Website:** [lohva.in](https://lohva.in) &nbsp;·&nbsp;
---

## What is CYRUS?

CYRUS is a personal AI assistant built for Windows — think JARVIS from Iron Man, running entirely on your machine. Wake it with a single word, speak any command naturally, and CYRUS handles the rest: launching apps, reading emails, messaging contacts, searching files, and answering anything — all hands free.

All AI processing runs **locally via Ollama**. Your voice never leaves your PC.

---

## Features

| # | Capability | Description |
|---|-----------|-------------|
| 01 | **Voice Control** | Say `"Nova"` to wake. Speak any command naturally — no keyboard, no clicks |
| 02 | **AI Brain** | Powered by Ollama LLM — runs 100% offline, no cloud required |
| 03 | **Messaging** | Send Telegram messages by voice. WhatsApp Web automation included |
| 04 | **Gmail** | Read unread emails aloud. Compose and send with a single spoken command |
| 05 | **System Control** | Open apps, adjust volume, monitor CPU/RAM, shutdown, sleep, and lock |
| 06 | **Live Weather** | Real-time conditions and 3-day forecasts for any city. No API key needed |
| 07 | **Memory** | Tell CYRUS to remember facts and reminders. Recall them anytime by asking |
| 08 | **File Search** | Find any file on your PC by name. Open folders and documents by voice |
| 09 | **Notion** | Create pages and search your entire Notion workspace by voice |

---

## How It Works

```
Say "Nova"  →  HUD appears  →  Speak command  →  CYRUS executes  →  Speaks back  →  HUD closes
```

1. **Wake** — Say `"Nova"` → Arc Reactor HUD appears on screen instantly
2. **Command** — Speak naturally. Vosk handles speech recognition fully offline
3. **Execute** — Command is routed to the correct handler (system / AI / messaging / web)
4. **Reply** — CYRUS speaks back, HUD closes, and waits for the next wake word

---

## Voice Commands

```bash
Nova → open chrome
Nova → weather in Chennai
Nova → system info
Nova → set volume to 50
Nova → check my emails
Nova → telegram John saying hello
Nova → shutdown in 30
Nova → lock screen
Nova → take a screenshot
Nova → remember my number is 9876543210
Nova → find resume file
Nova → who invented Python
Nova → create Notion note
Nova → open WhatsApp
Nova → play music on Spotify
```

---

## Installation

### Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Windows 10 / 11 |
| Python | 3.10 |
| RAM | 8 GB minimum — 16 GB recommended |
| Storage | 4 GB (including AI model) |
| Microphone | Any built-in or external mic |
| Internet | Only for search, weather, and messaging |

---

### Step 1 — Clone the repo

```cmd
git clone https://github.com/Lohith848/CYRUS.git
cd CYRUS
```

### Step 2 — Install dependencies

```cmd
py -3.10 -m pip install PySide6 pyttsx3 vosk pyaudio requests psutil pyautogui pycaw comtypes python-telegram-bot==13.15 pywhatkit notion-client google-auth google-auth-oauthlib google-api-python-client
```

### Step 3 — Download Vosk voice model

1. Go to [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
2. Download `vosk-model-en-in-0.5` (Indian English)
3. Extract to `C:\CYRUS\models\`

### Step 4 — Install Ollama (AI brain)

1. Download from [ollama.com](https://ollama.com)
2. Run:

```cmd
ollama serve
ollama pull llama3
```

### Step 5 — Configure settings

Edit `config/settings.json`:

```json
{
  "wake_word": "nova",
  "ollama_model": "llama3",
  "vosk_model_path": "C:/CYRUS/models/vosk-model-en-in-0.5",
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN",
    "default_chat_id": "YOUR_CHAT_ID"
  }
}
```

### Step 6 — Launch CYRUS

```cmd
py -3.10 launch.py
```

---

## Auto-start on Boot

Run once to add CYRUS to Windows startup:

```cmd
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "CYRUS" /t REG_SZ /d "wscript \"C:\CYRUS\START_CYRUS.vbs\"" /f
```

---

## Project Structure

```
CYRUS/
├── launch.py                   # Entry point
├── core/
│   ├── brain.py                # Ollama LLM integration
│   ├── command_handler.py      # Routes all commands
│   ├── command_router.py       # Pattern matching
│   ├── system_control.py       # App / system control
│   ├── voice.py                # TTS engine
│   └── voice_state.py          # Mic state management
├── voice/
│   └── listener.py             # Vosk speech recognition
├── ui/
│   ├── hud.py                  # Arc Reactor HUD overlay
│   └── tray.py                 # System tray icon
├── integrations/
│   ├── telegram_bot.py
│   ├── gmail_integration.py
│   ├── weather.py
│   ├── file_search.py
│   ├── messaging.py
│   └── notion_integration.py
├── memory/
│   └── memory_manager.py       # Persistent memory
└── config/
    └── settings.json           # Configuration
```

---

## Tech Stack

- [PySide6](https://doc.qt.io/qtforpython/) — Qt6 UI framework (Arc Reactor HUD)
- [Vosk](https://alphacephei.com/vosk/) — Fully offline speech recognition
- [Ollama](https://ollama.com) — Local LLM (llama3)
- [pyttsx3](https://pyttsx3.readthedocs.io/) — Text-to-speech engine
- [python-telegram-bot](https://python-telegram-bot.org/) — Telegram API
- [Google API Client](https://github.com/googleapis/google-api-python-client) — Gmail integration
- [Notion Client](https://github.com/ramnes/notion-sdk-py) — Notion API
- [Open-Meteo](https://open-meteo.com/) — Weather (no API key needed)

---

## Privacy

CYRUS is built **local-first**:

- Speech recognition runs **on-device** via Vosk
- AI inference runs **on-device** via Ollama
- Your voice, commands, and data **never leave your PC**
- Internet is used only when explicitly required (weather, messaging, search)

---

## System Requirements Summary

| Component | Spec |
|-----------|------|
| OS | Windows 10 / 11 |
| Python | 3.10 |
| RAM | 8 GB min — 16 GB recommended |
| Storage | 4 GB (including AI model) |
| Microphone | Built-in or external |
| Wake Word | `"Nova"` |
| AI Engine | Ollama — 100% offline |
| Voice Model | Vosk `en-in` — Indian English |
| UI | PySide6 (Qt6) |

---

> **CYRUS — Personal AI Assistant · Built for Windows by Lohith.**
