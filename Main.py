"""
╔══════════════════════════════════════════════════════════════╗
║            J A R V I S   A I   2 . 0                        ║
║         by Darshan I H  |  github.com/darshan3751            ║
╚══════════════════════════════════════════════════════════════╝

Entry point.  Run:  python Main.py
"""

import os
import sys
import threading
import time

from dotenv import load_dotenv
load_dotenv()

# ── Backend imports ──────────────────────────────────────────
from Backend.SpeechEngine   import listen, speak
from Backend.Brain          import decide
from Backend.Automation     import execute
from Backend.GestureControl import StartGestureMode, StopGestureMode, IsGestureRunning
from Backend.YouTubePlayer  import PlayYouTubeSong, SearchAndListYouTube

# ── GUI (optional – runs in own thread) ─────────────────────
try:
    from Frontend.GUI import start_gui
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

WAKE_WORD = os.getenv("WAKE_WORD", "jarvis")


def process_command(text: str) -> bool:
    """
    Pipeline: raw text → brain decision → executor → TTS reply.
    Returns False when user says "exit" / "quit" / "goodbye".
    """
    text = text.strip().lower()

    # Hard-stop words
    if any(w in text for w in ["exit", "quit", "goodbye", "bye jarvis"]):
        speak("Goodbye! Have a great day.")
        if IsGestureRunning():
            StopGestureMode()
        return False

    # Decision layer
    decision = decide(text)
    print(f"[Brain] Decision → {decision}")

    # Execute & get spoken reply
    reply = execute(decision, text)
    if reply:
        speak(reply)

    return True


def main():
    speak("Hello! Jarvis AI 2.0 online. How can I help you?")
    print("\n[Jarvis 2.0] Listening… say the wake word or type a command.")

    running = True
    while running:
        try:
            user_input = listen()           # returns transcribed text or ""
            if not user_input:
                continue
            print(f"[You] {user_input}")
            if WAKE_WORD in user_input.lower() or True:   # always active mode
                running = process_command(user_input)
        except KeyboardInterrupt:
            speak("Shutting down. Goodbye!")
            if IsGestureRunning():
                StopGestureMode()
            sys.exit(0)
        except Exception as e:
            print(f"[Main] Error: {e}")
            time.sleep(0.5)


if __name__ == "__main__":
    if GUI_AVAILABLE:
        gui_thread = threading.Thread(target=start_gui, daemon=True)
        gui_thread.start()
    main()
