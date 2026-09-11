import math

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QLinearGradient,
    QRadialGradient,
    QFont,
)

from PySide6.QtWidgets import QWidget


class VoiceVisualizer(QWidget):
    """
    Animated HUD inspired by the uploaded JARVIS reference.

    This is intentionally drawn with QPainter, so no extra
    animation library is required.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = "READY"
        self.phase = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

        self.setMinimumSize(420, 420)

    def set_state(self, state):
        self.state = state.upper()
        self.update()

    def animate(self):
        self.phase += 0.055
        if self.phase > math.tau * 100:
            self.phase = 0
        self.update()

    def _accent(self):
        if self.state == "LISTENING":
            return QColor(75, 235, 255)
        if self.state == "THINKING":
            return QColor(125, 170, 255)
        if self.state == "RESPONSE":
            return QColor(100, 255, 205)
        return QColor(85, 210, 255)

    def paintEvent(self, event):
        del event

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2 - 15

        # Background
        background = QLinearGradient(0, 0, 0, h)
        background.setColorAt(0.0, QColor("#02060b"))
        background.setColorAt(0.5, QColor("#07121a"))
        background.setColorAt(1.0, QColor("#010306"))
        painter.fillRect(self.rect(), background)

        accent = self._accent()

        # Very subtle HUD grid
        painter.setPen(QPen(QColor(30, 75, 90, 45), 1))

        grid_step = 45

        for x in range(0, w, grid_step):
            painter.drawLine(x, 0, x, h)

        for y in range(0, h, grid_step):
            painter.drawLine(0, y, w, y)

        # Subtle center crosshair
        painter.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), 70), 1))
        painter.drawLine(cx - 245, cy, cx + 245, cy)
        painter.drawLine(cx, cy - 245, cx, cy + 245)

        # Outer glow rings
        for ring in range(5):
            pulse = (math.sin(self.phase * 1.4 + ring * 0.8) + 1) / 2
            radius = 115 + ring * 31 + pulse * 8

            alpha = max(20, 80 - ring * 10)

            painter.setPen(
                QPen(
                    QColor(
                        accent.red(),
                        accent.green(),
                        accent.blue(),
                        alpha
                    ),
                    2 if ring < 2 else 1
                )
            )

            painter.drawEllipse(
                QRectF(
                    cx - radius,
                    cy - radius,
                    radius * 2,
                    radius * 2
                )
            )

        # Rotating segmented ring
        painter.save()
        painter.translate(cx, cy)

        rotation = math.degrees(self.phase * 0.65)
        painter.rotate(rotation)

        segment_radius = 170

        for i in range(24):
            angle = i * 15
            painter.save()
            painter.rotate(angle)

            active = (
                i % 3 == int(self.phase * 2) % 3
                or self.state == "LISTENING" and i % 2 == 0
            )

            if active:
                alpha = 230
                width = 4
            else:
                alpha = 85
                width = 2

            painter.setPen(
                QPen(
                    QColor(
                        accent.red(),
                        accent.green(),
                        accent.blue(),
                        alpha
                    ),
                    width
                )
            )

            painter.drawLine(
                0,
                -segment_radius,
                0,
                -segment_radius + (18 if active else 11)
            )

            painter.restore()

        painter.restore()

        # Small rotating markers
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-math.degrees(self.phase * 0.9))

        for i in range(8):
            angle = i * 45
            painter.save()
            painter.rotate(angle)

            marker_color = QColor(
                accent.red(),
                accent.green(),
                accent.blue(),
                190 if i % 2 == 0 else 90
            )

            painter.setPen(QPen(marker_color, 2))
            painter.drawLine(0, -205, 0, -220)

            painter.restore()

        painter.restore()

        # Central energy halo
        halo_radius = 92 + (
            math.sin(self.phase * 3.0) + 1
        ) * 7

        halo = QRadialGradient(cx, cy, halo_radius)
        halo.setColorAt(
            0.0,
            QColor(
                accent.red(),
                accent.green(),
                accent.blue(),
                115
            )
        )
        halo.setColorAt(
            0.45,
            QColor(
                accent.red(),
                accent.green(),
                accent.blue(),
                45
            )
        )
        halo.setColorAt(
            1.0,
            QColor(0, 0, 0, 0)
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(halo))

        painter.drawEllipse(
            QRectF(
                cx - 130,
                cy - 130,
                260,
                260
            )
        )

        # Central core
        core_radius = 72 + (
            math.sin(self.phase * 3.5) + 1
        ) * 3

        core = QRadialGradient(
            cx - 15,
            cy - 20,
            core_radius
        )

        core.setColorAt(
            0.0,
            QColor(225, 255, 255, 245)
        )
        core.setColorAt(
            0.18,
            QColor(
                accent.red(),
                accent.green(),
                accent.blue(),
                230
            )
        )
        core.setColorAt(
            0.55,
            QColor(
                accent.red(),
                accent.green(),
                accent.blue(),
                100
            )
        )
        core.setColorAt(
            1.0,
            QColor(0, 0, 0, 0)
        )

        painter.setBrush(QBrush(core))
        painter.setPen(
            QPen(
                QColor(
                    accent.red(),
                    accent.green(),
                    accent.blue(),
                    230
                ),
                2
            )
        )

        painter.drawEllipse(
            QRectF(
                cx - core_radius,
                cy - core_radius,
                core_radius * 2,
                core_radius * 2
            )
        )

        # Inner core rings
        for radius in (44, 30, 17):
            painter.setBrush(Qt.NoBrush)
            painter.setPen(
                QPen(
                    QColor(
                        225,
                        255,
                        255,
                        170 if radius != 17 else 230
                    ),
                    1
                )
            )
            painter.drawEllipse(
                QRectF(
                    cx - radius,
                    cy - radius,
                    radius * 2,
                    radius * 2
                )
            )

        # HAMMU text
        painter.setPen(QColor("#e8feff"))
        painter.setFont(
            QFont("Segoe UI", 11, QFont.Bold)
        )

        text_rect = QRectF(
            cx - 60,
            cy - 10,
            120,
            25
        )

        painter.drawText(
            text_rect,
            Qt.AlignCenter,
            "HAMMU"
        )

        # Voice waveform
        wave_y = cy + 250
        bar_count = 38
        spacing = 10
        total_width = (bar_count - 1) * spacing
        start_x = cx - total_width / 2

        for i in range(bar_count):
            wave = (
                math.sin(
                    self.phase * 4.0 +
                    i * 0.52
                ) +
                0.45 * math.sin(
                    self.phase * 7.0 +
                    i * 0.21
                )
            )

            amplitude = 7 + abs(wave) * 23

            if self.state == "LISTENING":
                amplitude *= 1.25
            elif self.state == "THINKING":
                amplitude *= 0.75
            elif self.state == "RESPONSE":
                amplitude *= 1.05

            painter.setPen(
                QPen(
                    QColor(
                        accent.red(),
                        accent.green(),
                        accent.blue(),
                        165
                    ),
                    3
                )
            )

            painter.drawLine(
                start_x + i * spacing,
                wave_y - amplitude,
                start_x + i * spacing,
                wave_y + amplitude
            )

        painter.end()