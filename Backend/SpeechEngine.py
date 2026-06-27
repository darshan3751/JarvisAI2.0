"""
Backend/SpeechEngine.py
════════════════════════
Speech-to-Text  : SpeechRecognition + Google API (free)
Text-to-Speech  : pyttsx3 (offline, fast) with fallback to gTTS
"""

import os
import io
import threading
import queue

import speech_recognition as sr

# ── TTS: pyttsx3 (offline) ──────────────────────────────────
try:
    import pyttsx3
    _engine = pyttsx3.init()
    _engine.setProperty("rate", 175)      # speaking speed
    _engine.setProperty("volume", 1.0)
    # Try to find a good English voice
    voices = _engine.getProperty("voices")
    for v in voices:
        if "english" in v.name.lower() or "david" in v.name.lower():
            _engine.setProperty("voice", v.id)
            break
    _PYTTSX3 = True
except Exception:
    _PYTTSX3 = False

# ── TTS fallback: gTTS + pygame ─────────────────────────────
try:
    from gtts import gTTS
    import pygame
    pygame.mixer.init()
    _GTTS = True
except ImportError:
    _GTTS = False

# ── STT ─────────────────────────────────────────────────────
_recognizer = sr.Recognizer()
_recognizer.pause_threshold  = 0.8
_recognizer.energy_threshold = 300
_recognizer.dynamic_energy_threshold = True


# ════════════════════════════════════════════════════════════
#  TTS
# ════════════════════════════════════════════════════════════

_speak_lock = threading.Lock()


def speak(text: str):
    """Convert text to speech (thread-safe)."""
    if not text:
        return
    print(f"[Jarvis] {text}")

    with _speak_lock:
        if _PYTTSX3:
            try:
                _engine.say(text)
                _engine.runAndWait()
                return
            except Exception as e:
                print(f"[TTS] pyttsx3 error: {e}")

        if _GTTS:
            try:
                tts = gTTS(text=text, lang="en", slow=False)
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                buf.seek(0)
                pygame.mixer.music.load(buf, "mp3")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                return
            except Exception as e:
                print(f"[TTS] gTTS error: {e}")

        # Last resort: print only
        print(f"[TTS FALLBACK] {text}")


# ════════════════════════════════════════════════════════════
#  STT
# ════════════════════════════════════════════════════════════

def listen(timeout: int = 5, phrase_limit: int = 8) -> str:
    """
    Listen via microphone and return transcribed text.
    Returns "" on failure / silence.
    """
    with sr.Microphone() as source:
        print("[STT] Listening…")
        try:
            _recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = _recognizer.listen(source, timeout=timeout,
                                        phrase_time_limit=phrase_limit)
        except sr.WaitTimeoutError:
            return ""

    try:
        text = _recognizer.recognize_google(audio, language="en-IN")
        print(f"[STT] Heard: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"[STT] Google API error: {e}")
        return ""
