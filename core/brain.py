"""core/brain.py — Ollama LLM"""
import requests, json

SYSTEM = (
    "You are CYRUS, a smart AI assistant on Windows. "
    "Reply in 1-2 short sentences. Call the user 'sir'. "
    "Be direct. Never say you cannot do something."
)


class Brain:
    def __init__(self):
        self.history = []
        try:
            with open("C:/CYRUS/config/settings.json") as f:
                s = json.load(f)
            self.model = s.get("ollama_model", "llama3")
            self.url   = s.get("ollama_url",   "http://localhost:11434")
        except Exception:
            self.model = "llama3"
            self.url   = "http://localhost:11434"

    def ask(self, prompt: str) -> str:
        if not self.is_alive():
            return ("Ollama is not running sir. "
                    "Please open a terminal and run: ollama serve")
        msgs = [{"role": "system", "content": SYSTEM}]
        msgs += self.history[-8:]
        msgs.append({"role": "user", "content": prompt})
        try:
            r = requests.post(
                f"{self.url}/api/chat",
                json={"model": self.model, "messages": msgs, "stream": False},
                timeout=60,
            )
            if r.status_code == 200:
                reply = r.json()["message"]["content"].strip()
                self.history.append({"role": "user",      "content": prompt})
                self.history.append({"role": "assistant", "content": reply})
                return reply
            if r.status_code == 404:
                return f"Model '{self.model}' not found. Run: ollama pull {self.model}"
            return f"Ollama error {r.status_code}."
        except requests.Timeout:
            return "Ollama is taking too long. Try ollama pull llama3."
        except Exception as exc:
            return f"Brain error: {exc}"

    def is_alive(self) -> bool:
        try:
            return requests.get(
                f"{self.url}/api/tags", timeout=2).status_code == 200
        except Exception:
            return False

    def clear(self) -> str:
        self.history.clear()
        return "Memory cleared sir."
