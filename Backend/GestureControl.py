"""
Backend/GestureControl.py  v2  –  Jarvis AI 2.0
═══════════════════════════════════════════════════
Gesture Map
───────────
SNAP (middle-finger rapid tap)    → Toggle gesture mode ON / OFF
Palm UP   (5 fingers, wrist low)  → Scroll UP   (velocity-aware)
Palm DOWN (5 fingers, wrist high) → Scroll DOWN
☝ Index ONLY – clockwise arc     → Volume UP  +3%
☝ Index ONLY – anticlockwise arc → Volume DOWN -3%
✌ Index + Middle                  → Play / Pause media
✊ Fist                           → Reset / clear state

pip install mediapipe opencv-python pyautogui pycaw comtypes
            screen-brightness-control
"""

from __future__ import annotations
import cv2, mediapipe as mp, pyautogui
import math, time, threading, collections, sys

pyautogui.FAILSAFE = False

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    _PYCAW = True
except ImportError:
    _PYCAW = False

try:
    import screen_brightness_control as sbc
    _SBC = True
except ImportError:
    _SBC = False

# ── Volume ──────────────────────────────────────────────────
_vol_obj = None
def _get_vol():
    global _vol_obj
    if _vol_obj: return _vol_obj
    if not _PYCAW: return None
    try:
        i = AudioUtilities.GetSpeakers().Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        _vol_obj = cast(i, POINTER(IAudioEndpointVolume))
    except Exception: pass
    return _vol_obj

def set_volume_delta(d: float):
    v = _get_vol()
    if v:
        v.SetMasterVolumeLevelScalar(max(0., min(1., v.GetMasterVolumeLevelScalar()+d/100)), None)
    else:
        pyautogui.press("volumeup" if d>0 else "volumedown")

def set_brightness_delta(d: float):
    if _SBC:
        try:
            cur = sbc.get_brightness(display=0)[0]
            sbc.set_brightness(max(0,min(100,cur+int(d))), display=0)
        except Exception as e: print(f"[Brightness] {e}")

# ── Geometry ─────────────────────────────────────────────────
def _fingers_up(lm, label):
    tips=[4,8,12,16,20]; pips=[3,7,11,15,19]
    up=[]
    up.append(lm[4].x < lm[3].x if label=="Right" else lm[4].x > lm[3].x)
    for t,p in zip(tips[1:],pips[1:]): up.append(lm[t].y < lm[p].y)
    return up

def _palm_up(lm): return lm[0].y > lm[9].y

def _signed_arc(pts):
    if len(pts)<5: return 0.
    s=0.
    for i in range(1,len(pts)-1):
        ax=pts[i][0]-pts[i-1][0]; ay=pts[i][1]-pts[i-1][1]
        bx=pts[i+1][0]-pts[i][0]; by=pts[i+1][1]-pts[i][1]
        s += ax*by - ay*bx
    return s

# ── Snap Detector ────────────────────────────────────────────
class SnapDetector:
    WIN=0.32; DROP=0.055; CD=1.3
    def __init__(self):
        self._base=None; self._down=False; self._dt=0.; self._last=0.
    def update(self, lm, fu):
        now=time.time(); n=sum(fu)
        if n==0 or n==5: self._base=None; self._down=False; return False
        y=lm[12].y
        if self._base is None: self._base=y; return False
        if not self._down and (y-self._base)>self.DROP:
            self._down=True; self._dt=now
        if self._down and y<(self._base+0.01):
            ok=time.time()-self._dt < self.WIN and now-self._last>self.CD
            self._down=False; self._base=y
            if ok: self._last=now; return True
        self._base=self._base*0.97+y*0.03
        return False

# ── Controller ───────────────────────────────────────────────
class GestureController:
    CAP_W=320; CAP_H=240; FPS=30; FINT=1/30
    SCROLL_N=200; SCROLL_F=550; VT=0.013; CS=0.28
    VS=3.; AL=24; AT=260; CV=0.22; CP=0.75

    def __init__(self, cam=0, preview=True):
        self.cam=cam; self.preview=preview
        self._run=False; self._on=False; self._t=None
        self._arc=collections.deque(maxlen=self.AL)
        self._py=None; self._ts=self._tv=self._tp=0.
        self._snap=SnapDetector()
        self._msg=""; self._mend=0.
        self._mp=mp.solutions.hands; self._draw=mp.solutions.drawing_utils

    def start(self):
        if self._run: return
        self._run=True; self._on=True
        self._t=threading.Thread(target=self._loop,daemon=True); self._t.start()
        print("[Gesture] Started - SNAP to toggle on/off.")

    def stop(self): self._run=False
    def is_running(self): return self._run
    def enable(self):  self._on=True;  self._flash("Gesture ON")
    def disable(self): self._on=False; self._flash("Gesture OFF")
    def toggle(self):
        if self._on: self.disable()
        else:        self.enable()

    def _flash(self, m, s=1.6):
        self._msg=m; self._mend=time.time()+s
        safe_msg = m.encode("ascii", errors="ignore").decode("ascii").strip()
        print(f"[Gesture] {safe_msg}")

    def _loop(self):
        bk = cv2.CAP_DSHOW if sys.platform=="win32" else cv2.CAP_ANY
        cap=cv2.VideoCapture(self.cam, bk)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,self.CAP_W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,self.CAP_H)
        cap.set(cv2.CAP_PROP_FPS,self.FPS)
        cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
        if not cap.isOpened():
            print("[Gesture] Camera not found."); self._run=False; return

        hands=self._mp.Hands(static_image_mode=False, max_num_hands=1,
            model_complexity=0, min_detection_confidence=0.68,
            min_tracking_confidence=0.62)
        tp=time.time()

        while self._run:
            now=time.time()
            wait=self.FINT-(now-tp)
            if wait>0: time.sleep(wait)
            tp=time.time()

            ret,frame=cap.read()
            if not ret: time.sleep(0.04); continue

            frame=cv2.flip(frame,1)
            rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            rgb.flags.writeable=False; res=hands.process(rgb); rgb.flags.writeable=True

            if res.multi_hand_landmarks and res.multi_handedness:
                hl=res.multi_hand_landmarks[0]
                lb=res.multi_handedness[0].classification[0].label
                lm=hl.landmark; fu=_fingers_up(lm,lb)
                if self._snap.update(lm,fu): self.toggle()
                if self.preview:
                    self._draw.draw_landmarks(frame,hl,self._mp.HAND_CONNECTIONS,
                        self._draw.DrawingSpec((0,200,80),1,3),
                        self._draw.DrawingSpec((220,50,50),1,2))
                if self._on: self._dispatch(lm,fu,frame)
            else:
                self._arc.clear(); self._py=None

            if self.preview:
                self._hud(frame); cv2.imshow("Jarvis 2.0 Gesture",frame)
                if cv2.waitKey(1)&0xFF==ord('q'): self.stop(); break

        cap.release(); hands.close()
        if self.preview: cv2.destroyAllWindows()

    def _dispatch(self, lm, fu, frame):
        now=time.time(); n=sum(fu); h,w,_=frame.shape
        self._arc.append((int(lm[8].x*w), int(lm[8].y*h)))

        # Two fingers -> play/pause
        if fu[1] and fu[2] and not fu[3] and not fu[4]:
            if now-self._tp>self.CP:
                pyautogui.press("playpause"); self._tp=now; self._flash("Play/Pause")
            return

        # Open palm -> scroll
        if n==5:
            wy=lm[0].y
            vel=abs(wy-self._py) if self._py else 0.
            self._py=wy
            step=self.SCROLL_F if vel>self.VT else self.SCROLL_N
            if now-self._ts>self.CS:
                if _palm_up(lm): pyautogui.scroll(step);  self._flash(f"Scroll Up {step}px")
                else:            pyautogui.scroll(-step); self._flash(f"Scroll Down {step}px")
                self._ts=now
            return

        self._py=None

        # Index only -> volume arc
        if fu[1] and not fu[2] and not fu[3] and not fu[4]:
            arc=_signed_arc(list(self._arc))
            if abs(arc)>self.AT and now-self._tv>self.CV:
                if arc>0: set_volume_delta(+self.VS); self._flash(f"Volume +{self.VS}%")
                else:     set_volume_delta(-self.VS); self._flash(f"Volume -{self.VS}%")
                self._arc.clear(); self._tv=now
            return

        # Fist -> clear
        if n==0: self._arc.clear(); self._py=None

    def _hud(self, frame):
        h,w=frame.shape[:2]; now=time.time()
        on=self._on
        c=(0,200,60) if on else (50,50,220)
        cv2.rectangle(frame,(0,0),(w,28),(15,15,15),-1)
        cv2.putText(frame,f"Gesture {'ON' if on else 'OFF'}  |  Snap=toggle  |  Q=quit",
            (6,19),cv2.FONT_HERSHEY_SIMPLEX,0.43,c,1,cv2.LINE_AA)
        if now<self._mend:
            fade=min(1.,(self._mend-now)/0.5)
            cv2.putText(frame,self._msg,(6,h-10),
                cv2.FONT_HERSHEY_DUPLEX,0.72,(int(255*fade),int(200*fade),0),2,cv2.LINE_AA)


# ── Singleton ────────────────────────────────────────────────
_ctrl: GestureController|None = None

def StartGestureMode(cam=0, preview=True):
    global _ctrl
    if _ctrl and _ctrl.is_running(): _ctrl.enable(); return
    _ctrl=GestureController(cam,preview); _ctrl.start()

def StopGestureMode():
    global _ctrl
    if _ctrl: _ctrl.stop()

def IsGestureRunning(): return bool(_ctrl and _ctrl.is_running())

def BrightnessUp(s=10):   set_brightness_delta(+s)
def BrightnessDown(s=10): set_brightness_delta(-s)
def VolumeUp(s=10):       set_volume_delta(+s)
def VolumeDown(s=10):     set_volume_delta(-s)
