from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter,
    QFileDialog,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
)

from .search_bar import SearchBar
from .library_view import LibraryView
from .playback_controls import PlaybackControls
from .lyrics_view import LyricsView
from .title_bar import TitleBar
from ..core import library, search, lyrics, metadata


class AppWindow(QMainWindow):
    def __init__(self, conn, player):
        super().__init__()
        self.setWindowTitle("Music Player")
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parent.parent / ".." / "assets" / "icons" / "application.png")))
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(960, 640)
        self.setMinimumSize(860, 560)
        self.setStyleSheet(
            "QMainWindow {"
            "  background: #efefef;"
            "}"
            "QMenuBar {"
            "  background: #f7f7f7;"
            "  border-bottom: 1px solid rgba(0, 0, 0, 0.08);"
            "  padding: 4px 6px;"
            "}"
            "QMenuBar::item {"
            "  padding: 4px 8px;"
            "  background: transparent;"
            "  border-radius: 4px;"
            "}"
            "QMenuBar::item:selected {"
            "  background: rgba(0, 0, 0, 0.06);"
            "}"
            "QMenu {"
            "  background: #ffffff;"
            "  border: 1px solid rgba(0, 0, 0, 0.10);"
            "  padding: 4px;"
            "}"
            "QMenu::item {"
            "  padding: 4px 12px;"
            "}"
            "QMenu::item:selected {"
            "  background: rgba(0, 0, 0, 0.06);"
            "}"
        )

        self._conn = conn
        self._player = player
        self._current_lyrics = []
        self._current_lyrics_index = -1
        self._current_path = None
        self._cover_cache = {}
        self._last_query = ""
        self._cover_debug_shown = False
        self._shuffle_enabled = False
        self._repeat_mode = "list"

        central = QWidget(self)
        central.setStyleSheet("background: transparent;")
        outer_layout = QVBoxLayout(central)
        outer_layout.setContentsMargins(8, 8, 8, 8)
        outer_layout.setSpacing(0)

        inner = QWidget(central)
        inner.setAttribute(Qt.WA_StyledBackground, True)
        inner.setStyleSheet(
            "background: #f3f3f3;"
            "border: 1px solid rgba(0, 0, 0, 0.08);"
            "border-radius: 8px;"
        )
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        outer_layout.addWidget(inner)

        self._title_bar = TitleBar(inner)
        layout.addWidget(self._title_bar)

        search_row = QWidget(inner)
        search_layout = QHBoxLayout(search_row)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        self._search_bar = SearchBar(search_row, self._on_search)
        self._search_bar.setStyleSheet(
            "background: #f7f7f7;"
            "border: 1px solid rgba(0, 0, 0, 0.08);"
            "border-radius: 6px;"
            "padding: 4px;"
        )
        search_layout.addWidget(self._search_bar, 1)

        self._scan_button = QPushButton("扫描", search_row)
        self._scan_button.setFixedHeight(30)
        self._scan_button.clicked.connect(self._scan_folder)
        self._scan_button.setStyleSheet(
            "QPushButton {"
            "  background: #f7f7f7;"
            "  border: 1px solid rgba(0, 0, 0, 0.08);"
            "  border-radius: 6px;"
            "  padding: 0 12px;"
            "}"
            "QPushButton:hover {"
            "  background: rgba(0, 0, 0, 0.04);"
            "}"
            "QPushButton:pressed {"
            "  background: rgba(0, 0, 0, 0.08);"
            "}"
        )
        search_layout.addWidget(self._scan_button)

        layout.addWidget(search_row)

        splitter = QSplitter(Qt.Horizontal, inner)
        splitter.setStyleSheet(
            "QSplitter::handle {"
            "  background: rgba(0, 0, 0, 0.06);"
            "  width: 1px;"
            "}"
        )
        self._library = LibraryView(splitter, self._on_activate, self._on_remove_selected)
        self._lyrics = LyricsView(splitter)
        splitter.addWidget(self._library)
        splitter.addWidget(self._lyrics)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

        self._controls = PlaybackControls(
            inner,
            on_toggle=self._on_toggle_playback,
            on_stop=self._on_stop,
            on_seek=self._on_seek,
            on_volume=self._on_volume,
            on_toggle_shuffle=self._on_toggle_shuffle,
            on_toggle_repeat=self._on_toggle_repeat,
        )
        self._controls.setStyleSheet(
            "background: #f7f7f7;"
            "border: 1px solid rgba(0, 0, 0, 0.08);"
            "border-radius: 6px;"
            "padding: 4px;"
        )
        layout.addWidget(self._controls)

        self.setCentralWidget(central)

        toggle_action = QAction(self)
        toggle_action.setShortcut(QKeySequence(Qt.Key_Space))
        toggle_action.triggered.connect(self._on_toggle_playback)
        self.addAction(toggle_action)

        next_action = QAction(self)
        next_action.setShortcut(QKeySequence(Qt.Key_Right))
        next_action.triggered.connect(self._on_next_track)
        self.addAction(next_action)

        prev_action = QAction(self)
        prev_action.setShortcut(QKeySequence(Qt.Key_Left))
        prev_action.triggered.connect(self._on_previous_track)
        self.addAction(prev_action)

        self._refresh_library()

        self._timer = QTimer(self)
        self._timer.setInterval(300)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        default_volume = 100
        self._controls.set_volume(default_volume)
        self._player.set_volume(default_volume)
        self._controls.set_shuffle_enabled(self._shuffle_enabled)
        self._controls.set_repeat_mode(self._repeat_mode)

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
        self._last_query = query
        self._refresh_library(query)

    def _on_activate(self, path: str):
        self._current_path = path
        self._player.load(path)
        self._player.play()
        self._controls.set_is_playing(True)
        self._current_lyrics = lyrics.load_lrc_for_track(path)
        self._current_lyrics_index = -1
        self._lyrics.set_lines([text for _ts, text in self._current_lyrics])

        cover_pixmap = None
        cached = self._cover_cache.get(path)
        if cached is not None:
            cover_pixmap = cached
        else:
            cover_bytes = metadata.read_embedded_cover(Path(path))
            if cover_bytes:
                pixmap = QPixmap()
                if pixmap.loadFromData(cover_bytes):
                    cover_pixmap = pixmap
            self._cover_cache[path] = cover_pixmap

        self._lyrics.set_cover(cover_pixmap)

        track = library.get_track_by_path(self._conn, path)
        if track is None:
            self._lyrics.set_track_info("", "", "", None)
        else:
            self._lyrics.set_track_info(
                track["title"],
                track["artist"],
                track["album"],
                track["duration"],
            )

    def _clear_current_track(self):
        self._current_path = None
        self._current_lyrics = []
        self._current_lyrics_index = -1
        self._controls.set_is_playing(False)
        self._lyrics.set_lines([])
        self._lyrics.set_cover(None)
        self._lyrics.set_track_info("", "", "", None)

    def _on_remove_selected(self, paths: list[str]):
        unique_paths = list(dict.fromkeys(paths))
        if not unique_paths:
            return
        confirm = QMessageBox.question(
            self,
            "从库中移除",
            f"将从库中移除 {len(unique_paths)} 首歌曲记录。磁盘文件不会被删除。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        deleted = library.remove_tracks(self._conn, unique_paths)
        for path in unique_paths:
            self._cover_cache.pop(path, None)
        if self._current_path in unique_paths:
            self._on_stop()
            self._clear_current_track()
        self._refresh_library(self._last_query)
        if deleted > 0:
            QMessageBox.information(self, "移除完成", f"已移除 {deleted} 首歌曲")

    def _on_toggle_playback(self):
        if self._player.is_playing():
            self._player.pause()
            self._controls.set_is_playing(False)
        else:
            self._player.play()
            self._controls.set_is_playing(True)

    def _on_stop(self):
        self._player.stop()
        self._controls.set_is_playing(False)

    def _on_seek(self, fraction: float):
        self._player.set_position(fraction)

    def _on_volume(self, value: int):
        self._player.set_volume(value)

    def _on_next_track(self):
        self._library.activate_next(mode=self._repeat_mode, shuffle_enabled=self._shuffle_enabled)

    def _on_previous_track(self):
        self._library.activate_previous(mode=self._repeat_mode, shuffle_enabled=self._shuffle_enabled)

    def _on_toggle_shuffle(self):
        self._shuffle_enabled = not self._shuffle_enabled
        self._controls.set_shuffle_enabled(self._shuffle_enabled)

    def _on_toggle_repeat(self):
        self._repeat_mode = "single" if self._repeat_mode == "list" else "list"
        self._controls.set_repeat_mode(self._repeat_mode)

    def _tick(self):
        if self._current_path:
            current = self._player.get_time_seconds()
            total = self._player.get_length_seconds()
            fraction = 0.0
            if total > 0:
                fraction = current / total
            self._controls.set_position(fraction, current, total)
            self._controls.set_is_playing(self._player.is_playing())

            if total > 0 and current >= (total - 0.2) and not self._player.is_playing():
                self._on_next_track()
                return

            if self._current_lyrics:
                index = lyrics.get_index_at_time(self._current_lyrics, current)
                if index != self._current_lyrics_index:
                    self._current_lyrics_index = index
                    self._lyrics.set_current_index(index)
            else:
                self._lyrics.set_current_index(-1)
