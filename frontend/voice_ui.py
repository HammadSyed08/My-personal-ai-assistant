# frontend/voice_ui.py

import math

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush,
    QLinearGradient, QRadialGradient, QConicalGradient,
    QFont, QPixmap, QPolygonF,
)
from PySide6.QtWidgets import QWidget


# ---------------------------------------------------------------------------
#  Palette
# ---------------------------------------------------------------------------

STATE_COLORS = {
    "READY":     QColor(90, 215, 255),
    "LISTENING": QColor(70, 240, 255),
    "THINKING":  QColor(130, 175, 255),
    "RESPONSE":  QColor(95, 255, 200),
    "ERROR":     QColor(255, 110, 110),
}


def _with_alpha(color, alpha):
    return QColor(
        color.red(), color.green(), color.blue(),
        max(0, min(255, int(alpha))),
    )


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return QColor(
        int(a.red()   + (b.red()   - a.red())   * t),
        int(a.green() + (b.green() - a.green()) * t),
        int(a.blue()  + (b.blue()  - a.blue())  * t),
        int(a.alpha() + (b.alpha() - a.alpha()) * t),
    )


# ---------------------------------------------------------------------------
#  VoiceVisualizer
# ---------------------------------------------------------------------------

class VoiceVisualizer(QWidget):
    """
    JARVIS-grade HUD.

    Public API (unchanged):
        set_state(str)
        start_boot()
        boot_finished  (Signal)
    """

    boot_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = "READY"
        self.phase = 0.0

        self._accent = QColor(STATE_COLORS["READY"])
        self._accent_target = QColor(STATE_COLORS["READY"])

        # ---- live mic level (simulated envelope) ---------------------------
        self._level = 0.15

        # ---- boot animation -----------------------------------------------
        self._boot_t = 0.0
        self._boot_active = True

        # ---- caches --------------------------------------------------------
        self._grid_cache = None
        self._grid_size = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

        self.setMinimumSize(420, 420)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)

    # -------------------------------------------------------------- API

    def set_state(self, state):
        self.state = state.upper()
        self._accent_target = QColor(
            STATE_COLORS.get(self.state, STATE_COLORS["READY"])
        )
        self.update()

    def start_boot(self):
        self._boot_t = 0.0
        self._boot_active = True
        self._accent = QColor(20, 60, 80)
        self.update()

    # ---------------------------------------------------------- animation

    def animate(self):
        self.phase += 0.055
        if self.phase > math.tau * 100:
            self.phase = 0

        if self._boot_active:
            self._boot_t = min(1.0, self._boot_t + 0.017)
            if self._boot_t >= 1.0:
                self._boot_active = False
                self.boot_finished.emit()

        # smooth state transition
        self._accent = _mix(self._accent, self._accent_target, 0.12)

        # update simulated mic level
        self._level = self._simulated_level(self.phase)

        self.update()

    # --------------------------------------------------------- helpers

    def _simulated_level(self, t):
        """Return 0..1 pseudo-audio level for the current state."""
        if self.state == "LISTENING":
            base = 0.55 + 0.32 * math.sin(t * 3.2)
            noise = 0.15 * math.sin(t * 11.7) * math.sin(t * 5.3)
            return max(0.18, min(1.0, base + noise))
        if self.state == "RESPONSE":
            return 0.35 + 0.22 * math.sin(t * 4.6)
        if self.state == "THINKING":
            return 0.22 + 0.12 * math.sin(t * 1.9)
        return 0.10 + 0.05 * math.sin(t * 1.2)

    def _boot_amounts(self):
        t = self._boot_t
        if t >= 1.0:
            return 1.0, 0.0
        eased = 1.0 - (1.0 - t) ** 3
        reveal = 0.10 + 0.90 * eased
        flash = max(0.0, 1.0 - t / 0.25) ** 2
        return reveal, flash

    def _grid_pixmap(self, w, h):
        if self._grid_cache is not None and self._grid_size == (w, h):
            return self._grid_cache

        pm = QPixmap(w, h)
        pm.fill(Qt.transparent)

        p = QPainter(pm)
        p.setPen(QPen(QColor(30, 75, 90, 120), 1))
        step = 45
        for x in range(0, w + step, step):
            p.drawLine(x, 0, x, h)
        for y in range(0, h + step, step):
            p.drawLine(0, y, w, y)

        p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        mask = QRadialGradient(w / 2.0, h / 2.0, max(w, h) * 0.62)
        mask.setColorAt(0.0, QColor(0, 0, 0, 255))
        mask.setColorAt(0.55, QColor(0, 0, 0, 150))
        mask.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(0, 0, w, h, QBrush(mask))
        p.end()

        self._grid_cache = pm
        self._grid_size = (w, h)
        return pm

    # -------------------------------------------------------- paint event

    def paintEvent(self, event):
        del event

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0 - 15.0
        s = max(0.62, min(1.65, min(w, h) / 560.0))

        reveal, flash = self._boot_amounts()
        accent = self._accent

        # ---- background ---------------------------------------------------
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0.0, QColor("#02060b"))
        bg.setColorAt(0.5, QColor("#07121a"))
        bg.setColorAt(1.0, QColor("#010306"))
        painter.fillRect(self.rect(), bg)

        # ---- HUD stack ----------------------------------------------------
        painter.save()
        painter.setOpacity(reveal)

        painter.drawPixmap(0, 0, self._grid_pixmap(w, h))

        self._paint_hud_frame(painter, w, h, accent)
        self._paint_crosshair(painter, cx, cy, s, accent)
        self._paint_outer_telemetry(painter, cx, cy, s, accent)
        self._paint_glow_rings(painter, cx, cy, s, accent)
        self._paint_segmented_ring(painter, cx, cy, s, accent)
        self._paint_markers(painter, cx, cy, s, accent)
        self._paint_halo(painter, cx, cy, s, accent)
        self._paint_audio_ring(painter, cx, cy, s, accent)
        self._paint_mic_activity(painter, cx, cy, s, accent)
        self._paint_core(painter, cx, cy, s, accent)
        self._paint_waveform(painter, cx, cy, s, accent)
        self._paint_labels(painter, w, h, accent)

        painter.restore()

        # ---- boot effects -------------------------------------------------
        if self._boot_t < 1.0:
            self._paint_boot_sweep(painter, w, h, accent)
        if flash > 0.0:
            self._paint_flash(painter, cx, cy, w, h, flash, accent)

        painter.end()

    # ------------------------------------------------------- HUD pieces

    def _paint_hud_frame(self, painter, w, h, accent):
        m = 16.0
        ln = 30.0
        pen = QPen(_with_alpha(accent, 130), 1.6)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        for x, y, dx, dy in (
            (m, m, 1, 1), (w - m, m, -1, 1),
            (m, h - m, 1, -1), (w - m, h - m, -1, -1),
        ):
            painter.drawLine(QPointF(x, y), QPointF(x + ln * dx, y))
            painter.drawLine(QPointF(x, y), QPointF(x, y + ln * dy))

    def _paint_crosshair(self, painter, cx, cy, s, accent):
        pen = QPen(_with_alpha(accent, 55), 1)
        pen.setStyle(Qt.CustomDashLine)
        pen.setDashPattern([2, 7])
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        ext = 260 * s
        gap = 115 * s
        painter.drawLine(QPointF(cx - ext, cy), QPointF(cx - gap, cy))
        painter.drawLine(QPointF(cx + gap, cy), QPointF(cx + ext, cy))
        painter.drawLine(QPointF(cx, cy - ext), QPointF(cx, cy - gap))
        painter.drawLine(QPointF(cx, cy + gap), QPointF(cx, cy + ext))

    def _paint_outer_telemetry(self, painter, cx, cy, s, accent):
        """Precision tick ring with degree numbers."""
        painter.save()
        painter.translate(cx, cy)

        # Every 5° → tiny tick, every 15° → medium, every 30° → numbered
        for deg in range(0, 360, 5):
            painter.save()
            painter.rotate(deg)

            if deg % 30 == 0:
                r0, r1, w = 232 * s, 244 * s, 1.6
                a = 200
            elif deg % 15 == 0:
                r0, r1, w = 235 * s, 242 * s, 1.2
                a = 140
            else:
                r0, r1, w = 238 * s, 241 * s, 1.0
                a = 70

            painter.setPen(QPen(_with_alpha(accent, a), w))
            painter.drawLine(QPointF(0, -r0), QPointF(0, -r1))
            painter.restore()

        # Degree numbers every 30°
        font = QFont("Consolas", max(6, int(7 * s)))
        font.setLetterSpacing(QFont.AbsoluteSpacing, 1)
        painter.setFont(font)
        painter.setPen(_with_alpha(accent, 165))

        for deg in range(0, 360, 30):
            painter.save()
            painter.rotate(deg)
            painter.translate(0, -254 * s)
            painter.rotate(-deg)          # keep numbers upright
            painter.drawText(
                QRectF(-16, -8, 32, 16),
                Qt.AlignCenter,
                f"{deg:03d}",
            )
            painter.restore()

        painter.restore()

    def _paint_glow_rings(self, painter, cx, cy, s, accent):
        painter.setBrush(Qt.NoBrush)

        for ring in range(5):
            pulse = (math.sin(self.phase * 1.4 + ring * 0.8) + 1) / 2
            radius = (115 + ring * 31 + pulse * 8) * s
            alpha = max(18, 72 - ring * 11)
            width = 2.0 if ring < 2 else 1.0

            painter.setPen(QPen(_with_alpha(accent, alpha), width))
            painter.drawEllipse(
                QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
            )

        # radar sweep on the inner ring
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(self.phase * 1.15))
        r = 115 * s
        pen = QPen(_with_alpha(accent, 180), 2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(QRectF(-r, -r, 2 * r, 2 * r), 0, int(70 * 16))
        painter.restore()

    def _paint_segmented_ring(self, painter, cx, cy, s, accent):
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(self.phase * 0.65))

        radius = 175 * s
        step = self.phase * 2

        for i in range(24):
            painter.save()
            painter.rotate(i * 15)

            active = (
                i % 3 == int(step) % 3
                or (self.state == "LISTENING" and i % 2 == 0)
            )
            alpha = 235 if active else 80
            width = 4.0 if active else 1.6
            length = 20 * s if active else 11 * s

            pen = QPen(_with_alpha(accent, alpha), width)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(QPointF(0, -radius), QPointF(0, -radius + length))
            painter.restore()

        painter.restore()

    def _paint_markers(self, painter, cx, cy, s, accent):
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-math.degrees(self.phase * 0.9))

        for i in range(8):
            painter.save()
            painter.rotate(i * 45)
            pen = QPen(
                _with_alpha(accent, 200 if i % 2 == 0 else 90), 2
            )
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(QPointF(0, -208 * s), QPointF(0, -224 * s))
            painter.restore()

        painter.restore()

    def _paint_halo(self, painter, cx, cy, s, accent):
        halo_radius = (92 + (math.sin(self.phase * 3.0) + 1) * 7) * s
        extent = 130 * s

        halo = QRadialGradient(cx, cy, halo_radius)
        halo.setColorAt(0.00, _with_alpha(accent, 115))
        halo.setColorAt(0.45, _with_alpha(accent, 45))
        halo.setColorAt(1.00, QColor(0, 0, 0, 0))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(halo))
        painter.drawEllipse(
            QRectF(cx - extent, cy - extent, extent * 2, extent * 2)
        )

    def _paint_audio_ring(self, painter, cx, cy, s, accent):
        """Radial audio-level bars around the core."""
        bars = 60
        r_inner = 132 * s
        max_len = 28 * s
        level = self._level

        for i in range(bars):
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(i * (360.0 / bars))

            seed = i * 0.61
            variance = 0.55 + 0.45 * math.sin(self.phase * 3.0 + seed)

            length = max(1.5, max_len * level * variance)

            alpha = int(80 + 160 * level * variance)
            alpha = max(60, min(255, alpha))
            width = 2.2 if length > 8 * s else 1.5

            pen = QPen(_with_alpha(accent, alpha), width)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)

            painter.drawLine(
                QPointF(0, -r_inner),
                QPointF(0, -r_inner - length),
            )
            painter.restore()

    def _paint_mic_activity(self, painter, cx, cy, s, accent):
        """Expanding radar pings — only while LISTENING."""
        if self.state != "LISTENING":
            return

        painter.setBrush(Qt.NoBrush)

        for offset in (0.0, 0.34, 0.67):
            t = (self.phase * 0.32 + offset) % 1.0
            r = (95 + t * 190) * s
            alpha = int(200 * (1 - t) ** 2)

            if alpha <= 3:
                continue

            pen = QPen(_with_alpha(accent, alpha), 2)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawEllipse(
                QRectF(cx - r, cy - r, r * 2, r * 2)
            )

    def _paint_core(self, painter, cx, cy, s, accent):
        core_radius = (72 + (math.sin(self.phase * 3.5) + 1) * 3) * s

        core = QRadialGradient(cx - 15 * s, cy - 20 * s, core_radius)
        core.setColorAt(0.00, QColor(225, 255, 255, 245))
        core.setColorAt(0.18, _with_alpha(accent, 230))
        core.setColorAt(0.55, _with_alpha(accent, 100))
        core.setColorAt(1.00, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(core))
        painter.setPen(QPen(_with_alpha(accent, 230), 2))
        painter.drawEllipse(
            QRectF(
                cx - core_radius, cy - core_radius,
                core_radius * 2, core_radius * 2,
            )
        )

        painter.setBrush(Qt.NoBrush)
        for radius in (44, 30, 17):
            r = radius * s
            painter.setPen(QPen(
                QColor(225, 255, 255, 170 if radius != 17 else 230), 1
            ))
            painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # soft glow behind wordmark
        glow_r = 74 * s
        glow = QRadialGradient(cx, cy, glow_r)
        glow.setColorAt(0.0, _with_alpha(accent, 70))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(
            QRectF(cx - glow_r, cy - glow_r, glow_r * 2, glow_r * 2)
        )

        # wordmark
        font = QFont("Segoe UI", max(8, int(11 * s)), QFont.Bold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 3.0)
        painter.setFont(font)
        painter.setPen(QColor("#eafeff"))
        painter.drawText(
            QRectF(cx - 80, cy - 11 * s, 160, 22 * s),
            Qt.AlignCenter,
            "HAMMU",
        )

    def _paint_waveform(self, painter, cx, cy, s, accent):
        wave_y = cy + 252 * s
        bar_count = 42
        spacing = 9.5 * s
        total_width = (bar_count - 1) * spacing
        start_x = cx - total_width / 2

        for i in range(bar_count):
            wave = (
                math.sin(self.phase * 4.0 + i * 0.52)
                + 0.45 * math.sin(self.phase * 7.0 + i * 0.21)
            )
            amp = (7 + abs(wave) * 23)

            if self.state == "LISTENING":
                amp *= 1.25
            elif self.state == "THINKING":
                amp *= 0.75
            elif self.state == "RESPONSE":
                amp *= 1.05

            amp *= s
            x = start_x + i * spacing

            glow = QPen(_with_alpha(accent, 45), 3 * s * 2.2)
            glow.setCapStyle(Qt.RoundCap)
            painter.setPen(glow)
            painter.drawLine(
                QPointF(x, wave_y - amp * 0.5),
                QPointF(x, wave_y + amp * 0.5),
            )

            pen = QPen(_with_alpha(accent, 195), 3 * s)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(
                QPointF(x, wave_y - amp),
                QPointF(x, wave_y + amp),
            )

    def _paint_labels(self, painter, w, h, accent):
        font = QFont("Consolas", 8)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2.4)
        painter.setFont(font)

        painter.setPen(_with_alpha(accent, 135))
        painter.drawText(
            QRectF(30, 22, w - 60, 16),
            Qt.AlignLeft | Qt.AlignVCenter,
            "HAMMU // VOICE CORE",
        )

        painter.setPen(_with_alpha(accent, 200))
        painter.drawText(
            QRectF(30, 22, w - 60, 16),
            Qt.AlignRight | Qt.AlignVCenter,
            f"STATE :: {self.state}",
        )

        # bottom telemetry strip
        painter.setPen(_with_alpha(accent, 120))
        painter.drawText(
            QRectF(30, h - 40, w - 60, 16),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"MIC LVL  {int(self._level * 100):03d}%",
        )
        painter.drawText(
            QRectF(30, h - 40, w - 60, 16),
            Qt.AlignCenter,
            "48kHz  •  24-bit  •  STREAM ACTIVE",
        )
        painter.drawText(
            QRectF(30, h - 40, w - 60, 16),
            Qt.AlignRight | Qt.AlignVCenter,
            "UPLINK :: SECURE",
        )

    # ------------------------------------------------------ boot effects

    def _paint_boot_sweep(self, painter, w, h, accent):
        t = self._boot_t
        eased = 1.0 - (1.0 - t) ** 2
        y = h * eased

        band = QLinearGradient(0, y - 70, 0, y + 70)
        band.setColorAt(0.0, QColor(0, 0, 0, 0))
        band.setColorAt(0.5, _with_alpha(accent, 55))
        band.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setPen(Qt.NoPen)
        painter.fillRect(QRectF(0, y - 70, w, 140), QBrush(band))

        pen = QPen(_with_alpha(accent, 180), 1.5)
        painter.setPen(pen)
        painter.drawLine(QPointF(0, y), QPointF(w, y))

    def _paint_flash(self, painter, cx, cy, w, h, amount, accent):
        ring_r = max(w, h) * (0.10 + 0.45 * (1.0 - amount))
        pen = QPen(_with_alpha(accent, int(150 * amount)), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(
            QRectF(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2)
        )

        r = max(w, h) * (0.30 + 0.45 * (1.0 - amount))
        bloom = QRadialGradient(cx, cy, r)
        bloom.setColorAt(0.0, _with_alpha(QColor(255, 255, 255), int(120 * amount)))
        bloom.setColorAt(0.4, _with_alpha(accent, int(80 * amount)))
        bloom.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bloom))
        painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))