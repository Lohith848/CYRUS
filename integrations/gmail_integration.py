"""
integrations/gmail_integration.py
-----------------------------------
Gmail: read unread emails + send emails by voice.
Setup: place gmail_credentials.json in C:/CYRUS/config/
"""

import os, base64, pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]
CREDS  = "C:/CYRUS/config/gmail_credentials.json"
TOKEN  = "C:/CYRUS/config/gmail_token.json"


def _svc():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN):
        with open(TOKEN, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS):
                raise FileNotFoundError(
                    "Gmail credentials not found. "
                    "Download from Google Cloud Console and save as "
                    "C:/CYRUS/config/gmail_credentials.json"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN, "wb") as f:
            pickle.dump(creds, f)
    return build("gmail", "v1", credentials=creds)


def read_emails(max_results: int = 5) -> str:
    """Read unread emails — returns a spoken summary."""
    try:
        svc = _svc()
        res = svc.users().messages().list(
            userId="me", labelIds=["INBOX", "UNREAD"],
            maxResults=max_results
        ).execute()
        msgs = res.get("messages", [])
        if not msgs:
            return "You have no unread emails, sir."

        summaries = []
        for m in msgs[:3]:   # speak max 3 to keep it short
            data = svc.users().messages().get(
                userId="me", id=m["id"], format="metadata",
                metadataHeaders=["From", "Subject"]
            ).execute()
            h = {x["name"]: x["value"]
                 for x in data["payload"]["headers"]}
            sender  = h.get("From", "Unknown").split("<")[0].strip()
            subject = h.get("Subject", "No subject")
            summaries.append(f"{sender}: {subject}")

        total = len(msgs)
        reply = f"You have {total} unread email{'s' if total>1 else ''}. "
        reply += " | ".join(summaries[:3])
        if total > 3:
            reply += f" and {total-3} more."
        return reply

    except FileNotFoundError as e:
        return str(e)
    except Exception as e:
        return f"Gmail error: {e}"


def send_email(to: str, subject: str, body: str) -> str:
    """Send a plain text email."""
    try:
        svc = _svc()
        msg = MIMEMultipart()
        msg["to"]      = to
        msg["subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        svc.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        return f"Email sent to {to}."
    except FileNotFoundError as e:
        return str(e)
    except Exception as e:
        return f"Failed to send email: {e}"
