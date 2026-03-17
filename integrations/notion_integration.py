"""
integrations/notion_integration.py
------------------------------------
Notion: search pages, create quick notes by voice.
Set api_key in C:/CYRUS/config/settings.json
"""

import json, os, webbrowser

SETTINGS = "C:/CYRUS/config/settings.json"


def _client():
    from notion_client import Client
    with open(SETTINGS) as f:
        s = json.load(f)
    key = s.get("notion", {}).get("api_key", "")
    if not key or key == "YOUR_NOTION_API_KEY_HERE":
        raise ValueError(
            "Notion API key not set. "
            "Add it to C:/CYRUS/config/settings.json"
        )
    return Client(auth=key)


def search_notion(query: str) -> str:
    try:
        c = _client()
        res = c.search(query=query, page_size=5).get("results", [])
        if not res:
            return f"Nothing found in Notion for '{query}'."
        names = []
        for item in res:
            props = item.get("properties", {})
            title = props.get("title", {}).get("title", [])
            names.append(title[0]["plain_text"] if title else "Untitled")
        return f"Found in Notion: {', '.join(names)}."
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Notion search error: {e}"


def create_note(title: str, content: str = "") -> str:
    """Create a quick page in Notion inbox / first available database."""
    try:
        c = _client()
        # find first database
        dbs = c.search(filter={"property":"object","value":"database"},
                       page_size=1).get("results", [])
        if not dbs:
            webbrowser.open("https://www.notion.so")
            return ("No Notion database found. "
                    "Please add your database ID to settings.json.")
        db_id = dbs[0]["id"]
        c.pages.create(
            parent={"database_id": db_id},
            properties={
                "title": {"title": [{"text": {"content": title}}]}
            },
            children=[{
                "object": "block",
                "type":   "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text",
                                   "text": {"content": content or title}}]
                }
            }] if content else []
        )
        return f"Notion note created: '{title}'."
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Notion error: {e}"
