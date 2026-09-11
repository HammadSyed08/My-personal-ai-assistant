import sys
from window import HAMMUWindow


from PySide6.QtWidgets import (
    QApplication,
)


# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setApplicationName(
        "HAMMU"
    )

    window = HAMMUWindow()
    window.show()

    sys.exit(
        app.exec()
    )
