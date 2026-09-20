# frontend/app.py
import sys
import os

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from security.permissions import set_confirmation_mode
from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QApplication

from window  import HAMMUWindow
from splash  import CinematicSplash


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------

def main():
    set_confirmation_mode("frontend")
    app = QApplication(sys.argv)
    app.setApplicationName("HAMMU")

    # ---- Global fusion style (dark, sleek) -------------------------------
    try:
        app.setStyle("Fusion")
    except Exception:
        pass

    window = HAMMUWindow()
    splash = CinematicSplash()

    # ---- Reveal the main window with a smooth fade-in --------------------
    def reveal_window():
        window.setWindowOpacity(0.0)
        window.showMaximized()
        window.raise_()
        window.activateWindow()

        fade = QPropertyAnimation(window, b"windowOpacity")
        fade.setDuration(600)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.OutCubic)
        fade.start()

        # keep a reference so it isn't garbage-collected
        window._boot_fade = fade

        splash.close()

    splash.finished.connect(reveal_window)

    # ---- Safety net: if splash somehow stalls, force the window ----------
    def force_reveal():
        if splash.isVisible():
            reveal_window()
    QTimer.singleShot(CinematicSplash.DURATION_MS + 2000, force_reveal)

    # ---- Kick off the intro ----------------------------------------------
    splash.begin()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()