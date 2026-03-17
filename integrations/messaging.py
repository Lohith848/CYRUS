"""
integrations/messaging.py
--------------------------
WhatsApp: uses pywhatkit (most reliable method).
Telegram: opens web.
"""
import webbrowser, time


def send_whatsapp(contact: str, message: str) -> str:
    """
    Send WhatsApp message.
    Tries pywhatkit first, falls back to web + pyautogui.
    """
    # Method 1: pywhatkit (best — opens WhatsApp Web pre-filled)
    try:
        import pywhatkit
        # sendwhatmsg_instantly opens WhatsApp Web and sends message
        pywhatkit.sendwhatmsg_instantly(
            phone_no=contact if contact.startswith("+") else f"+91{contact}",
            message=message,
            wait_time=12,
            tab_close=True
        )
        return f"WhatsApp message sent to {contact}."
    except ImportError:
        pass   # pywhatkit not installed, try next method
    except Exception as e:
        print(f"[WA] pywhatkit error: {e}")

    # Method 2: pyautogui keyboard automation
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        webbrowser.open("https://web.whatsapp.com")
        time.sleep(5)   # wait for WhatsApp Web to load

        # search for contact using Ctrl+F shortcut
        pyautogui.hotkey("ctrl", "f")
        time.sleep(1.5)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.typewrite(contact, interval=0.1)
        time.sleep(2.5)
        pyautogui.press("enter")
        time.sleep(1.5)

        # click message box (Tab to message input)
        pyautogui.press("tab")
        time.sleep(0.5)
        pyautogui.typewrite(message, interval=0.06)
        time.sleep(0.5)
        pyautogui.press("enter")
        return f"Message sent to {contact} on WhatsApp."
    except ImportError:
        webbrowser.open("https://web.whatsapp.com")
        return f"Opened WhatsApp Web. Please send '{message}' to {contact} manually."
    except Exception as e:
        webbrowser.open("https://web.whatsapp.com")
        return f"Opened WhatsApp Web. Send '{message}' to {contact}."


def open_whatsapp(contact: str = "") -> str:
    webbrowser.open("https://web.whatsapp.com")
    if contact:
        return f"Opened WhatsApp Web. Search for {contact}."
    return "Opened WhatsApp Web."


def open_telegram() -> str:
    webbrowser.open("https://web.telegram.org")
    return "Opened Telegram Web."


def send_telegram(contact: str, message: str) -> str:
    webbrowser.open("https://web.telegram.org")
    return f"Opened Telegram Web. Send '{message}' to {contact}."
