<div align="center">

<img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&weight=700&size=36&pause=1000&color=2196F3&center=true&vCenter=true&width=700&lines=JARVIS+AI+2.0;Your+Intelligent+Desktop+Assistant;Built+by+Darshan+I+H" alt="Jarvis AI 2.0" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-LLaMA3-F55036?style=for-the-badge&logo=meta&logoColor=white)](https://groq.com)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Gestures-00897B?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/darshan3751/JarvisAI2.0?style=for-the-badge&color=FFD700)](https://github.com/darshan3751/JarvisAI2.0/stargazers)

<br/>

> **Jarvis AI 2.0** is a next-generation AI voice + gesture desktop assistant.  
> Talk to it. Wave at it. It listens, thinks, and acts — all in real time.

<br/>

[🚀 Quick Start](#-quick-start) · [✨ Features](#-features) · [🖐️ Gestures](#️-gesture-reference) · [🗣️ Commands](#️-voice-commands) · [📁 Structure](#-project-structure)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **AI Brain** | Groq LLaMA-3 routes every command with near-zero latency |
| 🎙️ **Voice Control** | Always-listening STT via Google Speech API |
| 🔊 **TTS Replies** | Natural pyttsx3 voice (offline, no lag) |
| 🖐️ **Gesture Control** | MediaPipe hand tracking — scroll, volume, play/pause |
| 👌 **Snap Toggle** | Snap your fingers to enable / disable gestures |
| 🎵 **YouTube Player** | Says a song name → opens directly on YouTube (no Google) |
| 🌤️ **Live Weather** | Real-time weather for any city |
| 🖥️ **System Control** | Volume, brightness, screenshots, app open/close |
| 📝 **Notes & Reminders** | Voice-set timed reminders, saved notes |
| 💬 **GUI** | Dark-mode CustomTkinter chat interface |
| ⚡ **Fast** | 320×240 capture + model_complexity=0 = smooth 30 fps |

---

## 🖐️ Gesture Reference

| Gesture | Action |
|---------|--------|
| 👌 **Snap** (middle finger rapid tap) | Toggle gesture mode **ON / OFF** |
| ✋ **Open palm UP** | Scroll **UP** (velocity-aware) |
| 🤚 **Open palm DOWN** | Scroll **DOWN** |
| ☝️ **Index – clockwise circle** | Volume **UP** +3% |
| ☝️ **Index – anticlockwise circle** | Volume **DOWN** -3% |
| ✌️ **Index + Middle up** | **Play / Pause** media |
| ✊ **Fist** | Reset / clear gesture state |

> Camera window shows a live HUD. Press **Q** to close it.

---

## 🗣️ Voice Commands

```
# YouTube
"Play Shape of You on YouTube"
"Play Believer by Imagine Dragons"
"Search YouTube for lo-fi study music"

# System
"Volume up / down / mute"
"Set volume to 60"
"Brightness up / down"
"Set brightness to 80"

# Gesture
"Start gesture mode"
"Stop gesture mode"

# Apps & Web
"Open Chrome"
"Open YouTube"
"Close Spotify"
"Search Python tutorials"

# Utilities
"Take a screenshot"
"What time is it"
"Weather in Bengaluru"
"Tell me a joke"
"Open the news"

# Notes & Reminders
"Note: buy groceries tomorrow"
"Remind me in 10 minutes to call mom"

# Chat
"Explain quantum computing"
"Write a Python function to sort a list"
```

---

## 🚀 Quick Start

### 1 — Clone
```bash
git clone https://github.com/darshan3751/JarvisAI2.0.git
cd JarvisAI2.0
```

### 2 — Install dependencies
```bash
pip install -r requirements.txt
```

> **Windows users:** Also install PyAudio via:  
> `pip install pipwin && pipwin install pyaudio`

### 3 — Configure API keys
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (free at console.groq.com)
```

### 4 — Run
```bash
python Main.py
```

---

## 📁 Project Structure

```
JarvisAI2.0/
│
├── Main.py                    # Entry point
│
├── Backend/
│   ├── Brain.py               # LLM-powered command router (Groq)
│   ├── Automation.py          # All action executors
│   ├── SpeechEngine.py        # STT (SpeechRecognition) + TTS (pyttsx3)
│   ├── GestureControl.py      # MediaPipe gestures + snap toggle
│   └── YouTubePlayer.py       # YouTube search → direct browser open
│
├── Frontend/
│   └── GUI.py                 # CustomTkinter dark-mode chat UI
│
├── Data/
│   ├── Notes.txt              # Saved voice notes
│   └── Screenshots/           # Auto-saved screenshots
│
├── .github/workflows/
│   └── ci.yml                 # GitHub Actions CI
│
├── .env.example               # API key template
├── requirements.txt
└── README.md
```

---

## 🧠 Architecture

```
You (voice/text)
      │
      ▼
 SpeechEngine (STT)
      │
      ▼
   Brain.py  ──► Groq LLaMA-3 ──► action tag
      │
      ▼
 Automation.py
   ├── YouTube Player
   ├── Gesture Controller  ◄── MediaPipe (camera thread)
   ├── System Controls
   ├── App Launcher
   └── LLM Chat fallback
      │
      ▼
 SpeechEngine (TTS) + GUI log
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Brain | Groq API · LLaMA 3 8B |
| Speech-to-Text | SpeechRecognition · Google API |
| Text-to-Speech | pyttsx3 (offline) · gTTS fallback |
| Gesture CV | MediaPipe · OpenCV |
| System Control | pycaw · screen-brightness-control · pyautogui |
| YouTube | youtubesearchpython |
| GUI | CustomTkinter |
| Language | Python 3.11+ |

---

## ⚡ Performance Tips

- Keep hand **30–60 cm** from camera for best gesture detection
- Say song name clearly: *"Play Blinding Lights by The Weeknd"*
- Snap gesture works **even when gesture mode is OFF** — it re-enables it
- Set `show_preview=False` in `StartGestureMode()` for ~10% CPU saving

---

## 🤝 Contributing

Pull requests welcome! Please open an issue first for major changes.

---

## 📄 License

MIT License — © 2025 [Darshan I H](https://github.com/darshan3751)

---

<div align="center">

Made with ❤️ by **Darshan I H**  
⭐ Star this repo if Jarvis helped you!

[![GitHub](https://img.shields.io/badge/GitHub-darshan3751-181717?style=for-the-badge&logo=github)](https://github.com/darshan3751)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Darshan_I_H-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/darshan-i-h-705287240/)

</div>
