"""
Backend/Automation.py
══════════════════════
Command executor for Jarvis AI 2.0.
Receives action tags from Brain.py and carries them out.
"""

from __future__ import annotations
import os
import re
import sys
import time
import datetime
import subprocess
import webbrowser
import pyautogui
import random

# Internal modules
from Backend.YouTubePlayer  import PlayYouTubeSong, SearchAndListYouTube
from Backend.GestureControl import (
    StartGestureMode, StopGestureMode,
    BrightnessUp, BrightnessDown, VolumeUp, VolumeDown,
)

# ── Optional: pycaw volume ───────────────────────────────────
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    _PYCAW = True
except ImportError:
    _PYCAW = False

# ── Optional: brightness ─────────────────────────────────────
try:
    import screen_brightness_control as sbc
    _SBC = True
except ImportError:
    _SBC = False

# ── Optional: weather ────────────────────────────────────────
try:
    import requests
    _REQUESTS = True
except ImportError:
    _REQUESTS = False


# ════════════════════════════════════════════════════════════
#  Helpers
# ════════════════════════════════════════════════════════════

def _open_app(name: str) -> str:
    name = name.strip().lower()
    # Browser shortcuts
    sites = {
        "youtube": "https://youtube.com",
        "google":  "https://google.com",
        "github":  "https://github.com",
        "gmail":   "https://mail.google.com",
        "maps":    "https://maps.google.com",
        "spotify": "https://open.spotify.com",
        "netflix": "https://netflix.com",
    }
    if name in sites:
        webbrowser.open(sites[name])
        return f"Opening {name}."

    # Windows apps
    apps_win = {
        "notepad":      "notepad.exe",
        "calculator":   "calc.exe",
        "paint":        "mspaint.exe",
        "cmd":          "cmd.exe",
        "terminal":     "wt.exe",
        "vs code":      "code",
        "chrome":       "chrome",
        "firefox":      "firefox",
        "file explorer":"explorer.exe",
        "task manager": "taskmgr.exe",
    }
    for key, cmd in apps_win.items():
        if key in name:
            try:
                subprocess.Popen(cmd, shell=True)
                return f"Opening {key}."
            except Exception as e:
                return f"Couldn't open {key}: {e}"

    # Fallback: try running it directly
    try:
        subprocess.Popen(name, shell=True)
        return f"Trying to open {name}."
    except Exception:
        return f"I couldn't find {name}."


def _close_app(name: str) -> str:
    name = name.strip().lower()

    if "camera" in name or "gesture" in name:
        try:
            from Backend.GestureControl import StopGestureMode, IsGestureRunning
            if IsGestureRunning():
                StopGestureMode()
        except:
            pass
        os.system("taskkill /f /im WindowsCamera.exe >nul 2>&1")
        return "Closed camera/gesture mode."

    aliases = {
        "chrome":   "chrome.exe",
        "google":   "chrome.exe",
        "browser":  "chrome.exe",
        "firefox":  "firefox.exe",
        "notepad":  "notepad.exe",
        "spotify":  "Spotify.exe",
        "discord":  "Discord.exe",
        "vs code":  "Code.exe",
        "edge":     "msedge.exe",
    }
    exe = aliases.get(name, name + ".exe")
    os.system(f"taskkill /f /im {exe} >nul 2>&1")
    return f"Closed {name}."


def _set_volume(val: int):
    if _PYCAW:
        try:
            devices = AudioUtilities.GetSpeakers()
            iface   = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            vol     = cast(iface, POINTER(IAudioEndpointVolume))
            vol.SetMasterVolumeLevelScalar(max(0, min(100, val)) / 100.0, None)
            return
        except Exception:
            pass
    pyautogui.press("volumemute")
    for _ in range(val // 5):
        pyautogui.press("volumeup")


def _get_weather(city: str) -> str:
    if not _REQUESTS:
        return "requests library not installed."
    key = os.getenv("OPENWEATHER_API_KEY", "")
    if not key:
        return "Set OPENWEATHER_API_KEY in your .env file."
    city = city.strip() or "Bengaluru"
    try:
        url  = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"
        data = requests.get(url, timeout=5).json()
        if data.get("cod") != 200:
            return f"Couldn't get weather for {city}."
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feel = data["main"]["feels_like"]
        hum  = data["main"]["humidity"]
        return (f"Weather in {city}: {desc}. "
                f"Temperature {temp}°C, feels like {feel}°C. "
                f"Humidity {hum}%.")
    except Exception as e:
        return f"Weather error: {e}"


JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "Why did the developer go broke? Because he used up all his cache!",
    "A SQL query walks into a bar, walks up to two tables and asks… Can I join you?",
    "There are 10 types of people: those who understand binary and those who don't.",
]


def _save_note(text: str) -> str:
    os.makedirs("Data", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("Data/Notes.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")
    return f"Note saved: {text}"


def _set_reminder(text: str) -> str:
    # Simple: parse "remind me in X minutes to Y"
    match = re.search(r"in (\d+) (minute|minutes|hour|hours)", text)
    if match:
        n    = int(match.group(1))
        unit = match.group(2)
        secs = n * 60 if "minute" in unit else n * 3600
        task = re.sub(r"remind me in \d+ (minute|minutes|hour|hours) (to )?", "", text).strip()

        def _fire():
            time.sleep(secs)
            try:
                from Backend.SpeechEngine import speak
                speak(f"Reminder: {task}")
            except Exception:
                print(f"[Reminder] {task}")

        import threading
        threading.Thread(target=_fire, daemon=True).start()
        return f"Reminder set for {n} {unit}: {task}."
    return "Please say 'remind me in X minutes to do something'."


# ════════════════════════════════════════════════════════════
#  Main executor
# ════════════════════════════════════════════════════════════

def execute(action: str, raw: str = "") -> str:
    """
    Route the action tag from Brain to the right handler.
    Returns a string reply for TTS (may be empty string).
    """
    a = action.strip().lower()

    # ── YouTube ──────────────────────────────────────────────
    if a.startswith("youtube play"):
        song = a.replace("youtube play", "").strip() or raw
        return PlayYouTubeSong(song)

    if a.startswith("youtube search"):
        q = a.replace("youtube search", "").strip() or raw
        return SearchAndListYouTube(q, count=3)

    # ── System: volume ───────────────────────────────────────
    if a == "system volume up":
        VolumeUp(10); return "Volume increased."
    if a == "system volume down":
        VolumeDown(10); return "Volume decreased."
    if a == "system volume mute":
        pyautogui.press("volumemute"); return "Volume toggled."
    if re.match(r"system volume \d+", a):
        val = int(a.split()[-1])
        _set_volume(val); return f"Volume set to {val} percent."

    # ── System: brightness ───────────────────────────────────
    if a == "system brightness up":
        BrightnessUp(10); return "Brightness increased."
    if a == "system brightness down":
        BrightnessDown(10); return "Brightness decreased."
    if re.match(r"system brightness \d+", a):
        val = int(a.split()[-1])
        if _SBC:
            sbc.set_brightness(max(0, min(100, val))); return f"Brightness set to {val}%."
        return "Brightness control not available."

    # ── Gesture mode ─────────────────────────────────────────
    if a == "gesture start":
        StartGestureMode()
        return "Gesture control activated. Snap your fingers to toggle it anytime."
    if a == "gesture stop":
        StopGestureMode(); return "Gesture control stopped."

    # ── Apps ─────────────────────────────────────────────────
    if a.startswith("open "):
        return _open_app(a[5:])
    if a.startswith("close "):
        return _close_app(a[6:])

    # ── Screenshot ───────────────────────────────────────────
    if a == "screenshot":
        os.makedirs("Data/Screenshots", exist_ok=True)
        fname = f"Data/Screenshots/{datetime.datetime.now():%Y%m%d_%H%M%S}.png"
        pyautogui.screenshot(fname)
        return f"Screenshot saved as {fname}."

    # ── Time / date ──────────────────────────────────────────
    if a == "time":
        now = datetime.datetime.now()
        return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d %Y')}."

    # ── Weather ──────────────────────────────────────────────
    if a.startswith("weather"):
        city = a.replace("weather", "").strip()
        return _get_weather(city)

    # ── Music media keys ─────────────────────────────────────
    if a == "music pause":
        pyautogui.press("playpause"); return "Media toggled."
    if a == "music next":
        pyautogui.press("nexttrack"); return "Next track."
    if a == "music prev":
        pyautogui.press("prevtrack"); return "Previous track."

    # ── Search ───────────────────────────────────────────────
    if a.startswith("search "):
        q = a[7:].strip()
        webbrowser.open(f"https://www.google.com/search?q={q.replace(' ', '+')}")
        return f"Searching Google for {q}."

    # ── Note ─────────────────────────────────────────────────
    if a.startswith("note "):
        return _save_note(a[5:].strip() or raw)

    # ── Reminder ─────────────────────────────────────────────
    if a.startswith("reminder "):
        return _set_reminder(a[9:].strip() or raw)

    # ── Joke ─────────────────────────────────────────────────
    if a == "joke":
        return random.choice(JOKES)

    # ── News ─────────────────────────────────────────────────
    if a == "news":
        webbrowser.open("https://news.google.com")
        return "Opening Google News for you."

    # ── General chat ─────────────────────────────────────────
    if a.startswith("general "):
        query = a[8:].strip() or raw
        return _llm_chat(query)

    # Fallback
    return _llm_chat(raw or action)


def _llm_chat(text: str) -> str:
    """Send a general question to Groq for a conversational answer."""
    try:
        from groq import Groq
        import os
        client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        resp   = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content":
                    "You are Jarvis AI 2.0, a helpful AI assistant. "
                    "Give concise answers (2-3 sentences max) suitable for text-to-speech."},
                {"role": "user", "content": text},
            ],
            temperature=0.7,
            max_tokens=150,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"I couldn't process that right now. Error: {e}"
