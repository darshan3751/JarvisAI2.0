# 🚀 GitHub Setup Guide — Jarvis AI 2.0

Follow these steps exactly to publish the project and update your profile.

---

## PART 1 — Create the new repo on GitHub

1. Go to https://github.com/new
2. Repository name: `JarvisAI2.0`
3. Description: `Next-gen AI desktop assistant with voice, gestures & YouTube control`
4. Set to **Public**
5. Do NOT tick "Add README" (we have one)
6. Click **Create repository**

---

## PART 2 — Push the project

Open terminal / cmd inside the `JarvisAI2.0/` folder:

```bash
git init
git add .
git commit -m "🚀 Initial release – Jarvis AI 2.0"
git branch -M main
git remote add origin https://github.com/darshan3751/JarvisAI2.0.git
git push -u origin main
```

Done! Your repo is live at https://github.com/darshan3751/JarvisAI2.0

---

## PART 3 — Update your GitHub profile README

1. Go to https://github.com/darshan3751/darshan3751
2. Click the pencil ✏️ icon to edit `README.md`
3. Select ALL (Ctrl+A) and DELETE everything
4. Paste the entire contents of `GITHUB_PROFILE_README.md`
5. Click **Commit changes** → **Commit directly to main**

Your profile at https://github.com/darshan3751 is now updated!

---

## PART 4 — Add repo topics (makes it discoverable)

1. Go to https://github.com/darshan3751/JarvisAI2.0
2. Click the ⚙️ gear icon next to "About"
3. Add topics: `python` `ai` `voice-assistant` `gesture-control` `mediapipe` `groq` `llm` `jarvis` `desktop-assistant` `opencv`
4. Save

---

## PART 5 — Pin the repo on your profile

1. Go to https://github.com/darshan3751
2. Click **Customize your pins**
3. Check `JarvisAI2.0` and `Jarvis.AI`
4. Save

---

## PART 6 — First run locally

```bash
# Clone your new repo
git clone https://github.com/darshan3751/JarvisAI2.0.git
cd JarvisAI2.0

# Install dependencies
pip install -r requirements.txt

# Windows PyAudio (if needed)
pip install pipwin
pipwin install pyaudio

# Set up API keys
cp .env.example .env
# Open .env and add: GROQ_API_KEY=your_key_from_console.groq.com

# Run!
python Main.py
```

---

## Free API Keys

| Service | Get key at | Free tier |
|---------|-----------|-----------|
| **Groq** (AI brain) | https://console.groq.com | ✅ Free, very fast |
| **OpenWeatherMap** | https://openweathermap.org/api | ✅ Free 1M calls/month |

---

That's it! 🎉
