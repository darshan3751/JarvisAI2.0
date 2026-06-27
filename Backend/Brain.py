"""
Backend/Brain.py
════════════════
Decision-making layer for Jarvis AI 2.0.
Uses Groq (fast LLM) to classify the user's intent into a clean
action string that Automation.py can execute.

Model used: llama3-8b-8192 (fast + free on Groq)
Fallback   : rule-based keyword matching (works offline)
"""

import os
import re
from groq import Groq

_client: Groq | None = None


def _get_client() -> Groq | None:
    global _client
    if _client:
        return _client
    key = os.getenv("GROQ_API_KEY", "")
    if key:
        _client = Groq(api_key=key)
    return _client


SYSTEM_PROMPT = """
You are the decision engine for Jarvis AI 2.0, an advanced AI desktop assistant.
Your job: read the user's query and return ONLY a short action tag from the list below.
No explanations. No punctuation. Just the action tag.

ACTION TAGS:
general <query>          - answer / chat (default)
open <app>               - open application or website
close <app>              - close application
search <query>           - google search
youtube play <song>      - play a song on YouTube
youtube search <query>   - search YouTube
system volume up         - increase volume
system volume down       - decrease volume
system volume mute       - mute/unmute
system volume <N>        - set volume to N percent
system brightness up     - increase screen brightness
system brightness down   - decrease screen brightness
system brightness <N>    - set brightness to N percent
gesture start            - start gesture control mode
gesture stop             - stop gesture control mode
weather <city>           - get weather info
reminder <text>          - set a reminder
note <text>              - save a note
screenshot               - take screenshot
joke                     - tell a joke
news                     - get latest news headlines
time                     - tell current time and date
music pause              - pause/play current media
music next               - skip to next track
music prev               - previous track

Examples:
User: "play Shape of You" → youtube play Shape of You
User: "turn up the volume" → system volume up
User: "make the screen brighter" → system brightness up
User: "start gesture mode" → gesture start
User: "what time is it" → time
User: "open chrome" → open chrome
User: "take a screenshot" → screenshot
"""


def _llm_decide(text: str) -> str:
    client = _get_client()
    if not client:
        return _rule_decide(text)
    try:
        resp = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": text},
            ],
            temperature=0,
            max_tokens=60,
        )
        return resp.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"[Brain] LLM error ({e}), falling back to rules.")
        return _rule_decide(text)


def _rule_decide(text: str) -> str:
    """Fast offline keyword matcher."""
    t = text.lower()

    if any(w in t for w in ["youtube", "play song", "play music", "play video"]):
        song = re.sub(r"(play|on youtube|youtube|song|music|video)", "", t).strip()
        return f"youtube play {song}" if song else "youtube search music"

    if "volume up" in t or "louder" in t or "increase volume" in t:
        return "system volume up"
    if "volume down" in t or "quieter" in t or "lower volume" in t:
        return "system volume down"
    if "mute" in t:
        return "system volume mute"

    if "brightness up" in t or "brighter" in t:
        return "system brightness up"
    if "brightness down" in t or "dimmer" in t or "dim screen" in t:
        return "system brightness down"

    if "gesture" in t and any(w in t for w in ["start", "on", "enable", "activate"]):
        return "gesture start"
    if "gesture" in t and any(w in t for w in ["stop", "off", "disable"]):
        return "gesture stop"

    if "screenshot" in t or "screen shot" in t:
        return "screenshot"
    if "time" in t or "date" in t:
        return "time"
    if "joke" in t:
        return "joke"
    if "weather" in t:
        city = re.sub(r"(weather|in|at|for|today)", "", t).strip()
        return f"weather {city}" if city else "weather"
    if "news" in t:
        return "news"
    if "pause" in t or "resume" in t:
        return "music pause"
    if "next song" in t or "next track" in t:
        return "music next"
    if any(t.startswith(w) for w in ["open ", "launch ", "start "]):
        app = re.sub(r"^(open|launch|start)\s+", "", t).strip()
        return f"open {app}"
    if any(t.startswith(w) for w in ["close ", "quit ", "exit "]):
        app = re.sub(r"^(close|quit|exit)\s+", "", t).strip()
        return f"close {app}"
    if "search" in t or "google" in t:
        query = re.sub(r"(search|google|for|on google)", "", t).strip()
        return f"search {query}"

    return f"general {text}"


def decide(text: str) -> str:
    """Public API: text → action string."""
    return _llm_decide(text)
