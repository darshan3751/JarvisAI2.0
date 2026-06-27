"""
Frontend/GUI.py  –  Jarvis AI 2.0
Modern dark GUI using CustomTkinter
pip install customtkinter
"""

import threading, datetime
try:
    import customtkinter as ctk
    _CTK = True
except ImportError:
    _CTK = False

def start_gui():
    if not _CTK:
        print("[GUI] Install customtkinter: pip install customtkinter")
        return
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Jarvis AI 2.0")
    root.geometry("700x500")
    root.resizable(False, False)

    # Header
    header = ctk.CTkLabel(root, text="⚡ JARVIS AI 2.0",
                          font=ctk.CTkFont(size=28, weight="bold"),
                          text_color="#2196F3")
    header.pack(pady=(20,5))

    sub = ctk.CTkLabel(root, text="Your Intelligent Desktop Assistant",
                       font=ctk.CTkFont(size=13), text_color="#888")
    sub.pack()

    # Chat area
    chat = ctk.CTkTextbox(root, width=660, height=300,
                          font=ctk.CTkFont(size=13), state="disabled",
                          fg_color="#1a1a2e", corner_radius=12)
    chat.pack(pady=15, padx=20)

    def log(who: str, msg: str):
        chat.configure(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M")
        chat.insert("end", f"[{ts}] {who}: {msg}\n")
        chat.see("end")
        chat.configure(state="disabled")

    # Input row
    frame = ctk.CTkFrame(root, fg_color="transparent")
    frame.pack(fill="x", padx=20, pady=5)

    entry = ctk.CTkEntry(frame, placeholder_text="Type a command…",
                         font=ctk.CTkFont(size=13), height=42, corner_radius=10)
    entry.pack(side="left", fill="x", expand=True, padx=(0,10))

    def send(_=None):
        text = entry.get().strip()
        if not text: return
        entry.delete(0, "end")
        log("You", text)
        def _run():
            from Backend.Brain import decide
            from Backend.Automation import execute
            from Backend.SpeechEngine import speak
            action = decide(text)
            reply  = execute(action, text)
            if reply:
                log("Jarvis", reply)
                speak(reply)
        threading.Thread(target=_run, daemon=True).start()

    entry.bind("<Return>", send)
    btn = ctk.CTkButton(frame, text="Send", width=90, height=42,
                        corner_radius=10, command=send,
                        fg_color="#2196F3", hover_color="#1565C0")
    btn.pack(side="left")

    # Status bar
    status = ctk.CTkLabel(root, text="🟢  Listening…",
                          font=ctk.CTkFont(size=11), text_color="#4CAF50")
    status.pack(pady=5)

    log("Jarvis", "Hello! Jarvis AI 2.0 is online. How can I help you?")
    root.mainloop()
