from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter,
    QFileDialog,
    QMessageBox,
)

from .search_bar import SearchBar
from .library_view import LibraryView
from .playback_controls import PlaybackControls
from .lyrics_view import LyricsView
from ..core import library, search, lyrics


class AppWindow(QMainWindow):
    def __init__(self, conn, player):
        super().__init__()
        self.setWindowTitle("Music Player")
        self.resize(900, 600)

        self._conn = conn
        self._player = player
        self._current_lyrics = []
        self._current_path = None

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        self._search_bar = SearchBar(central, self._on_search)
        layout.addWidget(self._search_bar)

        splitter = QSplitter(Qt.Horizontal, central)
        self._library = LibraryView(splitter, self._on_activate)
        self._lyrics = LyricsView(splitter)
        splitter.addWidget(self._library)
        splitter.addWidget(self._lyrics)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

        self._controls = PlaybackControls(
            central,
            on_play=self._on_play,
            on_pause=self._on_pause,
            on_stop=self._on_stop,
            on_seek=self._on_seek,
        )
        layout.addWidget(self._controls)

        self.setCentralWidget(central)

        file_menu = self.menuBar().addMenu("文件")
        scan_action = QAction("扫描文件夹", self)
        scan_action.triggered.connect(self._scan_folder)
        file_menu.addAction(scan_action)
        file_menu.addSeparator()
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        self._refresh_library()

        self._timer = QTimer(self)
        self._timer.setInterval(300)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _scan_folder(self):
        path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if not path:
            return
        folder = Path(path)
        try:
            count = library.scan_and_index(self._conn, folder)
        except Exception as exc:
            QMessageBox.critical(self, "扫描失败", str(exc))
            return
        QMessageBox.information(self, "扫描完成", f"已加入 {count} 首歌曲")
        self._refresh_library()

    def _refresh_library(self, query: str = ""):
        rows = library.search(self._conn, search.normalize_query(query))
        self._library.set_tracks(rows)

    def _on_search(self, query: str):
        self._refresh_library(query)

    def _on_activate(self, path: str):
        self._current_path = path
        self._player.load(path)
        self._player.play()
        self._current_lyrics = lyrics.load_lrc_for_track(path)
        if not self._current_lyrics:
            self._lyrics.set_line("")

    def _on_play(self):
        self._player.play()

    def _on_pause(self):
        self._player.pause()

    def _on_stop(self):
        self._player.stop()

    def _on_seek(self, fraction: float):
        self._player.set_position(fraction)

    def _tick(self):
        if self._current_path:
            current = self._player.get_time_seconds()
            total = self._player.get_length_seconds()
            fraction = 0.0
            if total > 0:
                fraction = current / total
            self._controls.set_position(fraction, current, total)

            if self._current_lyrics:
                line = lyrics.get_line_at_time(self._current_lyrics, current)
                self._lyrics.set_line(line)
