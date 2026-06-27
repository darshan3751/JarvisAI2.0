"""
Backend/YouTubePlayer.py  v2  –  Jarvis AI 2.0
════════════════════════════════════════════════
• Searches YouTube directly (no Google redirect)
• Opens result in default browser at youtube.com URL
• Respects voice command order — plays immediately, no confirmation
• Optional: yt-dlp + VLC for ad-free background playback
"""

from __future__ import annotations
import webbrowser, subprocess, threading, os, time

try:
    from youtubesearchpython import VideosSearch
    _YSP = True
except ImportError:
    _YSP = False
    print("[YouTube] Run: pip install youtubesearchpython")


def _search(query: str, n: int = 1) -> list[dict]:
    if not _YSP:
        return []
    try:
        r = VideosSearch(query, limit=n).result().get("result", [])
        return [{"title": v.get("title","?"), "url": v.get("link",""),
                 "channel": v.get("channel",{}).get("name",""),
                 "duration": v.get("duration","")} for v in r]
    except Exception as e:
        print(f"[YouTube] Search error: {e}"); return []


def _open(url: str):
    """Open a youtube.com URL directly — never google.com."""
    if not url.startswith("https://www.youtube.com"):
        print(f"[YouTube] Bad URL blocked: {url}"); return
    webbrowser.open(url)
    print(f"[YouTube] Opened: {url}")


def _try_vlc(url: str) -> bool:
    vlc_paths = [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        "/usr/bin/vlc", "/Applications/VLC.app/Contents/MacOS/VLC",
    ]
    vlc = next((p for p in vlc_paths if os.path.exists(p)), None)
    if not vlc:
        return False
    try:
        res = subprocess.run(["yt-dlp","-g","--format","best[height<=720]", url],
                             capture_output=True, text=True, timeout=12)
        stream = res.stdout.strip().split("\n")[0]
        if stream:
            subprocess.Popen([vlc, stream],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[YouTube] Streaming via VLC.")
            return True
    except Exception:
        pass
    return False


def PlayYouTubeSong(query: str, direct: bool = False) -> str:
    """Search and immediately play. Returns TTS string."""
    if not query.strip():
        return "Please tell me what song to play."
    print(f"[YouTube] Searching: {query}")
    hits = _search(query, n=1)
    if not hits:
        return f"Sorry, I couldn't find '{query}' on YouTube."
    v = hits[0]
    print(f"[YouTube] → {v['title']} | {v['url']}")
    if direct and _try_vlc(v["url"]):
        return f"Playing '{v['title']}' by {v['channel']} via VLC."
    threading.Thread(target=_open, args=(v["url"],), daemon=True).start()
    return f"Playing '{v['title']}' by {v['channel']} on YouTube."


def SearchAndListYouTube(query: str, count: int = 5) -> str:
    hits = _search(query, n=count)
    if not hits:
        return f"No results for '{query}'."
    lines = [f"Top {len(hits)} results for {query}:"]
    for i, v in enumerate(hits, 1):
        lines.append(f"{i}. {v['title']} – {v['channel']} ({v['duration']})")
    return "\n".join(lines)


def PlayYouTubeIndex(query: str, index: int = 1) -> str:
    hits = _search(query, n=index)
    if len(hits) < index:
        return f"Result {index} not found."
    v = hits[index-1]
    threading.Thread(target=_open, args=(v["url"],), daemon=True).start()
    return f"Playing result {index}: '{v['title']}' by {v['channel']}."
