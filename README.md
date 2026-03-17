# CYRUS — AI Assistant

> Voice-controlled AI assistant for Windows. Say **"Nova"** to wake it up.

🌐 **Website:** [lohva.in](https://lohva.in)

---

## What is CYRUS?

CYRUS is a personal AI assistant that runs on your Windows laptop — like JARVIS from Iron Man. It listens to your voice, executes commands, answers questions, sends messages, and controls your entire system — hands free.

---

## Features

| Feature | Description |
|---------|-------------|
| 🎤 Voice Control | Say "Nova" to wake. Speak any command naturally |
| 🧠 AI Brain | Powered by Ollama LLM — runs 100% offline |
| 📱 Messaging | Send Telegram messages by voice |
| 📧 Gmail | Read and send emails by voice |
| ⚡ System Control | Open apps, volume, shutdown, sleep, lock |
| 🌦️ Weather | Real-time weather for any city |
| 🧾 Memory | Remember facts and recall them anytime |
| 🔍 File Search | Find any file on your PC by name |
| 📝 Notion | Create and search Notion pages by voice |

---

## How It Works

```
Say "Nova"  →  HUD appears  →  Say command  →  CYRUS executes  →  HUD closes
```

1. **Wake** — Say "Nova" → Arc Reactor HUD appears on screen
2. **Command** — Speak any command naturally
3. **Execute** — CYRUS routes to the right handler instantly
4. **Reply** — Speaks back and closes the HUD

---

## Installation

### Requirements
- Windows 10 / 11
- Python 3.10
- Microphone

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

## Voice Commands

```
Nova → open chrome
Nova → weather in Chennai
Nova → system info
Nova → set volume to 50
Nova → check my emails
Nova → telegram John saying hello
Nova → shutdown in 30
Nova → remember my number is 9876543210
Nova → find resume file
Nova → who invented Python
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
├── launch.py              # Entry point
├── core/
│   ├── brain.py           # Ollama LLM integration
│   ├── command_handler.py # Routes all commands
│   ├── command_router.py  # Pattern matching
│   ├── system_control.py  # App/system control
│   ├── voice.py           # TTS engine
│   └── voice_state.py     # Mic state
├── voice/
│   └── listener.py        # Vosk speech recognition
├── ui/
│   ├── hud.py             # Arc Reactor HUD
│   └── tray.py            # System tray icon
├── integrations/
│   ├── telegram_bot.py    # Telegram API
│   ├── gmail_integration.py
│   ├── weather.py
│   ├── file_search.py
│   ├── messaging.py
│   └── notion_integration.py
├── memory/
│   └── memory_manager.py  # Persistent memory
└── config/
    └── settings.json      # Configuration
```

---

## Built With

- [PySide6](https://doc.qt.io/qtforpython/) — UI framework
- [Vosk](https://alphacephei.com/vosk/) — Offline speech recognition
- [Ollama](https://ollama.com) — Local LLM
- [pyttsx3](https://pyttsx3.readthedocs.io/) — Text to speech
- [python-telegram-bot](https://python-telegram-bot.org/) — Telegram API

---

## Website

Visit **[lohva.in](https://lohva.in)** to learn more about CYRUS.

---

Built by [Lohith](https://github.com/Lohith848)
