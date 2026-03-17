"""
integrations/weather.py
------------------------
Weather via wttr.in — no API key needed.
Falls back to simple format if JSON fails.
"""
import requests

def get_weather(city: str = "") -> str:
    city = city.strip()
    # simple one-line format — most reliable
    try:
        loc = city if city else ""
        url = f"https://wttr.in/{loc}?format=3"
        r = requests.get(url, timeout=8,
                         headers={"User-Agent": "curl/7.0"})
        if r.status_code == 200 and r.text.strip():
            line = r.text.strip()
            # line looks like: "Chennai, India: ⛅  +32°C"
            # clean it for TTS
            clean = line.replace("°C", " degrees celsius")
            clean = ''.join(c for c in clean if c.isascii() or c == ' ')
            clean = ' '.join(clean.split())
            return f"Weather: {clean}"
        return "Could not get weather right now."
    except requests.exceptions.ConnectionError:
        return "No internet connection to check weather."
    except Exception as e:
        return f"Weather error: {e}"


def get_forecast(city: str = "") -> str:
    city = city.strip()
    try:
        loc = city if city else ""
        url = f"https://wttr.in/{loc}?format=j1"
        r = requests.get(url, timeout=10,
                         headers={"User-Agent": "curl/7.0"})
        if r.status_code != 200:
            return get_weather(city)
        d = r.json()
        area = d["nearest_area"][0]["areaName"][0]["value"]
        lines = [f"Forecast for {area}:"]
        labels = ["Today", "Tomorrow", "Day after"]
        for i, w in enumerate(d["weather"][:3]):
            desc  = w["hourly"][4]["weatherDesc"][0]["value"]
            maxc  = w["maxtempC"]
            minc  = w["mintempC"]
            lines.append(f"{labels[i]}: {desc}, {minc} to {maxc} degrees.")
        return " ".join(lines)
    except Exception as e:
        return get_weather(city)
