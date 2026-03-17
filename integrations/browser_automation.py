"""
integrations/browser_automation.py
------------------------------------
Browser automation via Selenium for WhatsApp Web, Instagram, YouTube.
Uses Chrome. Make sure Chrome is installed.
"""

import time
import webbrowser


def _get_driver(headless=False):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service

    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--user-data-dir=C:/CYRUS/memory/chrome_profile")
    opts.add_argument("--profile-directory=Default")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)


# ── WhatsApp Web ───────────────────────────────────────────────────────────
def send_whatsapp(contact: str, message: str) -> str:
    """Send a WhatsApp message via WhatsApp Web."""
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys

        driver = _get_driver()
        driver.get("https://web.whatsapp.com")
        print("[WhatsApp] Waiting for QR scan / loading... (30s)")
        time.sleep(30)  # Time for QR scan if needed

        # Search contact
        wait = WebDriverWait(driver, 20)
        search = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
        ))
        search.click()
        search.send_keys(contact)
        time.sleep(2)

        # Click first result
        first = wait.until(EC.presence_of_element_located(
            (By.XPATH, f'//span[@title="{contact}"]')
        ))
        first.click()
        time.sleep(1)

        # Type and send message
        box = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
        ))
        box.send_keys(message)
        box.send_keys(Keys.ENTER)
        time.sleep(1)
        driver.quit()
        return f"WhatsApp message sent to {contact}."
    except ImportError:
        return "Selenium not installed. Run: pip install selenium webdriver-manager"
    except Exception as e:
        return f"WhatsApp error: {e}"


def open_whatsapp_chat(contact: str) -> str:
    """Open WhatsApp Web and search for a contact."""
    webbrowser.open("https://web.whatsapp.com")
    return f"Opened WhatsApp Web. Search for '{contact}' manually."


# ── YouTube ────────────────────────────────────────────────────────────────
def play_youtube(query: str) -> str:
    """Search YouTube and open first result."""
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        driver = _get_driver()
        driver.get(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        wait = WebDriverWait(driver, 10)

        # Click first video result
        first_video = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "ytd-video-renderer a#video-title")
        ))
        first_video.click()
        time.sleep(3)
        return f"Playing '{query}' on YouTube."
    except ImportError:
        webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        return f"Opened YouTube search for '{query}'."
    except Exception as e:
        webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        return f"Opened YouTube for '{query}'."


# ── Instagram ──────────────────────────────────────────────────────────────
def open_instagram_profile(username: str) -> str:
    webbrowser.open(f"https://www.instagram.com/{username}/")
    return f"Opened Instagram profile: @{username}"


def open_instagram_dm() -> str:
    webbrowser.open("https://www.instagram.com/direct/inbox/")
    return "Opened Instagram DMs."


# ── Telegram ───────────────────────────────────────────────────────────────
def open_telegram_web() -> str:
    webbrowser.open("https://web.telegram.org")
    return "Opened Telegram Web."


# ── Notion ─────────────────────────────────────────────────────────────────
def open_notion_page(page_name: str = "") -> str:
    if page_name:
        webbrowser.open(f"https://www.notion.so/search?q={page_name.replace(' ', '+')}")
        return f"Searching Notion for '{page_name}'."
    webbrowser.open("https://www.notion.so")
    return "Opened Notion."
