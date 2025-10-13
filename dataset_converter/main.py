import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from src.gui.home_window import HomeWindow


def ensure_data_dirs():
    base = Path(__file__).parent / "data"
    (base / "input").mkdir(parents=True, exist_ok=True)
    (base / "output").mkdir(parents=True, exist_ok=True)


def main():
    ensure_data_dirs()
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
