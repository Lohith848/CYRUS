"""
ui/hud.py — CYRUS HUD
Nova wake word → show → run command → hide. Clean and simple.
"""
import sys, os, math, threading, datetime, json
sys.path.insert(0, "C:/CYRUS")

from PySide6.QtWidgets import QApplication, QWidget, QLineEdit
from PySide6.QtCore    import Qt, QTimer, QPointF, QRectF, Signal, QObject
from PySide6.QtGui     import (QPainter, QColor, QPen, QBrush,
                               QRadialGradient, QFont)


class _Bus(QObject):
    reply    = Signal(str)
    status   = Signal(str)
    do_show  = Signal()
    do_hide  = Signal()

_bus = _Bus()


class CyrusHUD(QWidget):

    SIZE   = 320
    R_RING = 148
    R_ORB  = 95

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CYRUS")
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._angle  = 0.0
        self._pulse  = 0.6
        self._pd     = 0.014
        self._mic    = True
        self._status = "ONLINE"
        self._reply  = ""
        self._ralpha = 0
        self._drag   = None
        self._listener = None

        iw, ih = 148, 28
        self._inp = QLineEdit(self)
        self._inp.setGeometry((self.SIZE-iw)//2, self.SIZE//2+28, iw, ih)
        self._inp.setAlignment(Qt.AlignCenter)
        self._inp.setPlaceholderText("command...")
        self._inp.setStyleSheet("""
            QLineEdit {
                background: transparent; border: none;
                border-bottom: 1px solid rgba(255,255,255,40);
                color: rgba(255,255,255,200);
                font-family: 'Segoe UI'; font-size: 11px; letter-spacing: 2px;
            }
            QLineEdit::placeholder { color: rgba(255,255,255,55); }
        """)
        self._inp.returnPressed.connect(self._submit)

        sg = QApplication.primaryScreen().geometry()
        self.move(sg.width()//2 - self.SIZE//2,
                  sg.height()//2 - self.SIZE//2)

        # animation timer
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(16)

        # wire signals — all run on main thread
        _bus.reply.connect(self._on_reply)
        _bus.status.connect(self._on_status)
        _bus.do_show.connect(self._show_hud)
        _bus.do_hide.connect(self._hide_hud)

        # don't hide on init — show immediately, hide after each command
        QTimer.singleShot(600, self._start_voice)

    # ── show / hide (always on main thread via signal) ─────────────
    def _show_hud(self):
        self.show()
        self.raise_()
        self.activateWindow()
        print("[HUD] shown.")

    def _hide_hud(self):
        self.hide()
        print("[HUD] hidden.")

    # ── animation ──────────────────────────────────────────────────
    def _tick(self):
        self._angle = (self._angle + 0.5) % 360
        self._pulse += self._pd
        if self._pulse >= 1.0 or self._pulse <= 0.3:
            self._pd = -self._pd
        if self._ralpha > 0:
            self._ralpha = max(0, self._ralpha - 2)
        self.update()

    # ── paint ───────────────────────────────────────────────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        S = self.SIZE; cx = cy = S/2; C = QPointF(cx, cy)

        bg = QRadialGradient(C, S/2)
        bg.setColorAt(0.0, QColor(8,10,14)); bg.setColorAt(1.0, QColor(4,5,8))
        p.setBrush(QBrush(bg)); p.setPen(Qt.NoPen)
        p.drawEllipse(C, S/2-2, S/2-2)

        p.setPen(QPen(QColor(255,255,255,22),1)); p.setBrush(Qt.NoBrush)
        p.drawEllipse(C, self.R_RING, self.R_RING)

        rect = QRectF(cx-self.R_RING, cy-self.R_RING, self.R_RING*2, self.R_RING*2)
        p.setPen(QPen(QColor(220,220,220,210),1.5,Qt.SolidLine,Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        for i in range(3):
            p.drawArc(rect, int((self._angle+i*120)*16), int(90*16))

        p.setPen(Qt.NoPen)
        for i in range(3):
            rad = math.radians(self._angle+i*120)
            tx = cx+self.R_RING*math.cos(rad); ty = cy-self.R_RING*math.sin(rad)
            p.setBrush(QBrush(QColor(255,255,255,60))); p.drawEllipse(QPointF(tx,ty),5,5)
            p.setBrush(QBrush(QColor(255,255,255,230))); p.drawEllipse(QPointF(tx,ty),2.5,2.5)

        mic_on = self._mic
        gc = QColor(255,255,255,int(28*self._pulse)) if mic_on else QColor(180,40,30,int(25*self._pulse))
        rc = QColor(255,255,255,55) if mic_on else QColor(180,60,50,55)
        og = QRadialGradient(C, self.R_ORB+20)
        og.setColorAt(0,gc); og.setColorAt(1,QColor(0,0,0,0))
        p.setBrush(QBrush(og)); p.setPen(Qt.NoPen)
        p.drawEllipse(C, self.R_ORB+20, self.R_ORB+20)

        of = QRadialGradient(QPointF(cx-6,cy-8), self.R_ORB)
        of.setColorAt(0,QColor(22,25,32,245)); of.setColorAt(0.7,QColor(14,16,22,250))
        of.setColorAt(1,QColor(10,10,16,255))
        p.setBrush(QBrush(of)); p.setPen(QPen(rc,1))
        p.drawEllipse(C, self.R_ORB, self.R_ORB)

        p.setPen(QPen(QColor(255,255,255,220)))
        f = QFont("Segoe UI", 18, QFont.Bold)
        f.setLetterSpacing(QFont.AbsoluteSpacing, 7)
        p.setFont(f)
        p.drawText(QRectF(cx-90,cy-52,180,38), Qt.AlignCenter, "CYRUS")

        dc = (QColor(80,220,120) if self._status=="ONLINE"
              else QColor(255,180,40) if self._status=="THINKING"
              else QColor(100,160,255))
        p.setBrush(QBrush(dc)); p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx,cy-14), 3, 3)

        if self._ralpha > 0 and self._reply:
            p.setPen(QPen(QColor(200,200,200,self._ralpha)))
            p.setFont(QFont("Segoe UI",8))
            p.drawText(QRectF(cx-80,cy+60,160,36),
                       Qt.AlignCenter|Qt.TextWordWrap, self._reply[:80])
        p.end()

    def _on_reply(self, t):  self._reply = t; self._ralpha = 255
    def _on_status(self, s): self._status = s

    # ── orb = mic toggle ────────────────────────────────────────────
    def _orb_hit(self, x, y):
        c = self.SIZE/2
        return (x-c)**2+(y-c)**2 <= self.R_ORB**2

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            lp = e.position()
            if self._orb_hit(lp.x(), lp.y()):
                self._toggle_mic(); self._drag = None
            else:
                self._drag = e.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, e):
        if self._drag and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, _): self._drag = None

    def _toggle_mic(self):
        self._mic = not self._mic
        try:
            from core.voice_state import set_mic
            set_mic(self._mic)
        except Exception: pass
        try:
            from core.voice import speak_async
            speak_async("On." if self._mic else "Off.")
        except Exception: pass

    # ── text input ──────────────────────────────────────────────────
    def _submit(self):
        text = self._inp.text().strip()
        if not text: return
        self._inp.clear()
        self._run_command(text)

    # ── voice callback (from listener thread) ───────────────────────
    def _on_voice(self, text):
        _bus.reply.emit(text)
        self._run_command(text)

    # ── THE ONLY place commands are executed ────────────────────────
    def _run_command(self, text):
        """Run command in background. When done → emit do_hide."""
        def _worker():
            _bus.status.emit("THINKING")
            try:
                from core.command_handler import handle_command
                reply = handle_command(text)   # blocking: speaks then returns
            except Exception as exc:
                reply = f"Error: {exc}"
                try:
                    from core.voice import speak
                    from core.voice_state import set_mic
                    set_mic(True)
                    speak(reply)
                except Exception: pass

            _bus.reply.emit(reply or "Done.")
            _bus.status.emit("ONLINE")
            # ── hide HUD after command finishes ──
            _bus.do_hide.emit()

        threading.Thread(target=_worker, daemon=True).start()

    # ── voice listener ──────────────────────────────────────────────
    def _start_voice(self):
        def _init():
            try:
                with open("C:/CYRUS/config/settings.json") as f:
                    s = json.load(f)
            except Exception:
                s = {}
            try:
                from voice.listener import VoiceListener
                self._listener = VoiceListener(
                    model_path=s.get("vosk_model_path",
                                     "C:/CYRUS/models/vosk-model-en-in-0.5"))
                self._listener.start(
                    on_command = self._on_voice,
                    on_wake    = self._wake,
                    on_sleep   = None,   # listener no longer calls on_sleep
                )
            except Exception as exc:
                print(f"[HUD] voice error: {exc}")
        threading.Thread(target=_init, daemon=True).start()

    def _wake(self):
        """Called by listener when wake word heard."""
        _bus.do_show.emit()
        def _greet():
            try:
                from core.voice import speak
                speak("Yes sir.")
            except Exception: pass
        threading.Thread(target=_greet, daemon=True).start()

    def closeEvent(self, _):
        QApplication.quit()


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # tray icon — always visible
    try:
        from ui.tray import CyrusTray
        CyrusTray(app).show()
    except Exception as exc:
        print(f"[HUD] tray: {exc}")

    win = CyrusHUD()
    win.show()          # show HUD on startup
    win.raise_()
    win.activateWindow()
    sys.exit(app.exec())
