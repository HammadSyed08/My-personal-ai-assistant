# frontend/splash.py
import math

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush,
    QLinearGradient, QRadialGradient, QFont,
)
from PySide6.QtWidgets import QWidget

# ---------------------------------------------------------------------------
# Startup audio (safe import — won't crash if audio.py is missing)
# ---------------------------------------------------------------------------
try:
    import winsound
    from audio import STARTUP_SOUND
    HAS_AUDIO = True
except Exception as _audio_err:
    HAS_AUDIO = False
    STARTUP_SOUND = None
    print(f"Splash audio disabled: {_audio_err}")


class CinematicSplash(QWidget):
    """
    Full-screen cinematic boot sequence for HAMMU.

    Timeline (≈4.2 s):
        0.00 → 0.15  black screen + horizontal scan sweep
        0.15 → 0.45  holographic grid + HAMMU logo reveal
        0.35 → 0.90  init stages + progress bar filling
        0.90 → 1.00  white flash transition

    Emits:
        finished  — the moment the intro ends
    """

    finished = Signal()

    DURATION_MS = 4200

    STAGES = (
        (0.00, "BOOTING NEURAL CORE"),
        (0.18, "LOADING LANGUAGE MODELS"),
        (0.38, "CALIBRATING VOICE ENGINE"),
        (0.58, "SYNCING MEMORY BANKS"),
        (0.76, "ESTABLISHING SECURE UPLINK"),
        (0.92, "HAMMU ONLINE"),
    )

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setWindowTitle("HAMMU — Booting")

        self.t = 0.0
        self.elapsed_ms = 0
        self._done = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(16)          # ~60 fps

    # ------------------------------------------------------------------ API

    def begin(self):
        """Fullscreen cinematic boot — covers the entire laptop screen."""
        # True fullscreen (works on every DPI / multi-monitor setup)
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self._play_audio()

    # Optional: allow ESC to skip the intro
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.timer.stop()
            if not self._done:
                self._done = True
                self.finished.emit()
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------- internal

    def _play_audio(self):
        if not HAS_AUDIO or not STARTUP_SOUND:
            return
        try:
            winsound.PlaySound(
                STARTUP_SOUND,
                winsound.SND_FILENAME | winsound.SND_ASYNC,
            )
        except Exception as error:
            print(f"Startup sound warning: {error}")

    def _tick(self):
        self.elapsed_ms += 16
        self.t = min(1.0, self.elapsed_ms / self.DURATION_MS)
        self.update()

        if self.t >= 1.0 and not self._done:
            self._done = True
            self.timer.stop()
            QTimer.singleShot(420, self.finished.emit)

    def _current_stage(self):
        text = ""
        for threshold, message in self.STAGES:
            if self.t >= threshold:
                text = message
        return text

    # --------------------------------------------------------- paint event

    def paintEvent(self, event):
        del event

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)

        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        t = self.t

        accent = QColor(85, 210, 255)

        # ---------------- background --------------------------------
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0.0, QColor("#010205"))
        bg.setColorAt(0.5, QColor("#020810"))
        bg.setColorAt(1.0, QColor("#000000"))
        p.fillRect(self.rect(), bg)

        # ---------------- scan sweep (0.00 → 0.45) -------------------
        if t < 0.45:
            scan_p = t / 0.45
            scan_y = h * scan_p

            band = QLinearGradient(0, scan_y - 80, 0, scan_y + 80)
            band.setColorAt(0.0, QColor(0, 0, 0, 0))
            band.setColorAt(0.5, QColor(accent.red(), accent.green(), accent.blue(), 90))
            band.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.fillRect(QRectF(0, scan_y - 80, w, 160), QBrush(band))

            p.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), 220), 1.5))
            p.drawLine(QPointF(0, scan_y), QPointF(w, scan_y))

        # ---------------- holographic grid --------------------------
        if t > 0.12:
            self._draw_grid(p, w, h, accent, min(1.0, (t - 0.12) / 0.35))

        # ---------------- corner brackets + status bars -------------
        if t > 0.30:
            self._draw_chrome(p, w, h, accent, min(1.0, (t - 0.30) / 0.25))

        # ---------------- central logo ------------------------------
        if t > 0.18:
            logo_alpha = min(1.0, (t - 0.18) / 0.25)
            self._draw_logo(p, cx, cy, w, accent, logo_alpha, t)

        # ---------------- stage text --------------------------------
        if t > 0.35:
            stage_alpha = min(1.0, (t - 0.35) / 0.15)
            self._draw_stage(p, cx, cy, w, accent, stage_alpha)

        # ---------------- progress bar ------------------------------
        if t > 0.35:
            self._draw_progress(p, cx, cy, w, accent, t)

        # ---------------- white flash (0.90 → 1.00) -----------------
        if t > 0.90:
            flash = (t - 0.90) / 0.10
            p.fillRect(self.rect(), QColor(180, 240, 255, int(200 * flash)))

        p.end()

    # ------------------------------------------------------------ helpers

    def _draw_grid(self, p, w, h, accent, alpha):
        step = 60
        pen = QPen(QColor(accent.red(), accent.green(), accent.blue(), int(28 * alpha)), 1)
        p.setPen(pen)
        for x in range(0, w + step, step):
            p.drawLine(x, 0, x, h)
        for y in range(0, h + step, step):
            p.drawLine(0, y, w, y)

    def _draw_chrome(self, p, w, h, accent, alpha):
        m = 34
        ln = 46
        pen = QPen(QColor(accent.red(), accent.green(), accent.blue(), int(140 * alpha)), 2)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)

        for x, y, dx, dy in (
            (m, m, 1, 1),
            (w - m, m, -1, 1),
            (m, h - m, 1, -1),
            (w - m, h - m, -1, -1),
        ):
            p.drawLine(QPointF(x, y), QPointF(x + ln * dx, y))
            p.drawLine(QPointF(x, y), QPointF(x, y + ln * dy))

        # status text
        font = QFont("Consolas", 9)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 4)
        p.setFont(font)
        p.setPen(QColor(accent.red(), accent.green(), accent.blue(), int(180 * alpha)))

        p.drawText(
            QRectF(m + 24, h - m - 24, w - 2 * m - 48, 20),
            Qt.AlignLeft | Qt.AlignVCenter,
            "HAMMU // NEURAL CORE v1.0",
        )
        p.drawText(
            QRectF(m + 24, h - m - 24, w - 2 * m - 48, 20),
            Qt.AlignRight | Qt.AlignVCenter,
            "SECURE CONNECTION ESTABLISHED",
        )

    def _draw_logo(self, p, cx, cy, w, accent, alpha, t):
        # outer glow
        r = 260
        glow = QRadialGradient(cx, cy - 30, r)
        glow.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), int(130 * alpha)))
        glow.setColorAt(0.55, QColor(accent.red(), accent.green(), accent.blue(), int(35 * alpha)))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(QRectF(cx - r, cy - 30 - r, r * 2, r * 2))

        # concentric rings
        p.setBrush(Qt.NoBrush)
        for i, ring_r in enumerate((150, 195, 240)):
            a = int((110 - i * 28) * alpha)
            if a <= 0:
                continue
            p.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), a), 1.2))
            p.drawEllipse(QRectF(cx - ring_r, cy - 30 - ring_r, ring_r * 2, ring_r * 2))

        # rotating arcs
        p.save()
        p.translate(cx, cy - 30)
        p.rotate((t * 900) % 360)

        p.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), int(220 * alpha)), 3))
        p.drawArc(QRectF(-150, -150, 300, 300), 0, int(80 * 16))
        p.drawArc(QRectF(-150, -150, 300, 300), int(180 * 16), int(80 * 16))

        p.rotate(-(t * 540) % 360)
        p.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), int(160 * alpha)), 2))
        p.drawArc(QRectF(-195, -195, 390, 390), 0, int(40 * 16))
        p.drawArc(QRectF(-195, -195, 390, 390), int(120 * 16), int(40 * 16))
        p.drawArc(QRectF(-195, -195, 390, 390), int(240 * 16), int(40 * 16))
        p.restore()

        # wordmark
        font = QFont("Segoe UI", 68, QFont.Black)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 24)
        p.setFont(font)
        p.setPen(QColor(235, 254, 255, int(255 * alpha)))
        p.drawText(QRectF(0, cy - 120, w, 130), Qt.AlignCenter, "HAMMU")

        # subtitle
        font2 = QFont("Segoe UI", 12, QFont.DemiBold)
        font2.setLetterSpacing(QFont.AbsoluteSpacing, 12)
        p.setFont(font2)
        p.setPen(QColor(120, 200, 220, int(210 * alpha)))
        p.drawText(
            QRectF(0, cy - 20, w, 30),
            Qt.AlignCenter,
            "PERSONAL AI ASSISTANT",
        )

    def _draw_stage(self, p, cx, cy, w, accent, alpha):
        text = self._current_stage()
        font = QFont("Consolas", 11)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 5)
        p.setFont(font)
        p.setPen(QColor(accent.red(), accent.green(), accent.blue(), int(230 * alpha)))
        p.drawText(
            QRectF(0, cy + 110, w, 22),
            Qt.AlignCenter,
            f">  {text}",
        )

    def _draw_progress(self, p, cx, cy, w, accent, t):
        bar_w = min(560, int(w * 0.55))
        bar_h = 3
        bar_x = cx - bar_w / 2
        bar_y = cy + 155

        # track
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 45))
        p.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 2, 2)

        # fill
        prog = max(0.0, min(1.0, (t - 0.35) / 0.55))
        p.setBrush(accent)
        p.drawRoundedRect(QRectF(bar_x, bar_y, bar_w * prog, bar_h), 2, 2)

        # percentage
        font = QFont("Consolas", 9)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 3)
        p.setFont(font)
        p.setPen(QColor(accent.red(), accent.green(), accent.blue(), 200))
        p.drawText(
            QRectF(0, bar_y + 12, w, 20),
            Qt.AlignCenter,
            f"{int(prog * 100):03d}%",
        )