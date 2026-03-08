import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .data import db
from .core import library
from .core.player import Player
from .ui.app_window import AppWindow


def main():
    data_dir = Path(__file__).resolve().parent / ".." / "data"
    data_dir = data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "library.db"

    conn = db.connect(db_path)
    library.init_library(conn)

    player = Player()
    qt_app = QApplication(sys.argv)
    qt_app.setWindowIcon(QIcon(str(Path(__file__).resolve().parent / ".." / "assets" / "icons" / "application.png")))
    window = AppWindow(conn, player)
    window.show()
    sys.exit(qt_app.exec_())


if __name__ == "__main__":
    main()
