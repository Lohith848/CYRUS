"""
integrations/telegram_bot.py
=============================
Send Telegram messages via Bot API.
100% reliable — pure HTTP, no browser needed.
"""
import requests
import json

SETTINGS = "C:/CYRUS/config/settings.json"


def _load():
    with open(SETTINGS) as f:
        s = json.load(f)
    tg = s.get("telegram", {})
    token    = tg.get("bot_token", "").strip()
    default  = str(tg.get("default_chat_id", "")).strip()
    contacts = {k.lower(): str(v) for k, v in tg.get("contacts", {}).items()}
    if not token or "YOUR_BOT_TOKEN" in token:
        raise ValueError(
            "Telegram bot token not set in settings.json")
    return token, default, contacts


def send_message(contact: str, message: str) -> str:
    try:
        token, default_id, contacts = _load()
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
        return f"Telegram config error: {e}"

    # resolve contact → chat_id
    contact_lower = contact.lower().strip()
    chat_id = ""

    if contact_lower in ("me", "myself", "self", ""):
        chat_id = default_id
    elif contact_lower in contacts:
        chat_id = contacts[contact_lower]
    elif contact.lstrip("+-").isdigit():
        chat_id = contact
    else:
        # fuzzy match
        for name, cid in contacts.items():
            if contact_lower in name or name in contact_lower:
                chat_id = cid
                contact = name
                break
        if not chat_id:
            chat_id = default_id   # fallback: send to yourself

    if not chat_id:
        return (f"No chat ID for '{contact}'. "
                f"Add them to settings.json telegram.contacts.")

    print(f"[Telegram] sending to chat_id={chat_id}: {message[:40]}")

    url  = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": message},
            timeout=10
        )
        print(f"[Telegram] status={r.status_code} body={r.text[:120]}")

        if r.status_code == 200:
            return f"Telegram message sent to {contact}."
        elif r.status_code == 400:
            desc = r.json().get("description", "bad request")
            return f"Telegram error: {desc}"
        elif r.status_code == 401:
            return "Invalid bot token. Check settings.json."
        elif r.status_code == 403:
            return (f"Bot blocked by user or chat not found. "
                    f"Make sure {contact} has started your bot first.")
        else:
            return f"Telegram API error {r.status_code}: {r.text[:80]}"

    except requests.exceptions.ConnectionError:
        return "No internet connection."
    except requests.exceptions.Timeout:
        return "Telegram request timed out."
    except Exception as e:
        return f"Telegram error: {e}"


def send_to_self(message: str) -> str:
    return send_message("me", message)


def get_updates() -> str:
    try:
        token, _, _ = _load()
    except Exception as e:
        return f"Config error: {e}"
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{token}/getUpdates",
            timeout=8)
        results = r.json().get("result", [])
        if not results:
            return "No new Telegram messages."
        msgs = []
        for u in results[-3:]:
            msg  = u.get("message", {})
            name = msg.get("from", {}).get("first_name", "?")
            text = msg.get("text", "")
            if text:
                msgs.append(f"{name}: {text}")
        return ("Messages: " + " | ".join(msgs)) if msgs else "No messages."
    except Exception as e:
        return f"Error: {e}"


def list_contacts() -> str:
    try:
        _, _, contacts = _load()
        if not contacts:
            return "No contacts saved in settings.json."
        return "Telegram contacts: " + ", ".join(contacts.keys()) + "."
    except Exception as e:
        return f"Config error: {e}"
