import sys
from PyQt6.QtWidgets import QApplication

from gui import SummarizerApp


def main() -> None:
    """Точка входа в программу"""
    app = QApplication(sys.argv)
    window = SummarizerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
