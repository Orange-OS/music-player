from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QAbstractItemView,
    QLabel,
)


class LyricsView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._cover_label = QLabel(self)
        self._cover_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self._cover_label.setFixedSize(160, 160)
        layout.addWidget(self._cover_label, alignment=Qt.AlignHCenter)

        self._title_artist_label = QLabel(self)
        self._album_duration_label = QLabel(self)
        info_font = self._title_artist_label.font()
        info_font.setPointSize(info_font.pointSize() + 1)
        for label in (self._title_artist_label, self._album_duration_label):
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setFont(info_font)
        layout.addWidget(self._title_artist_label)
        layout.addWidget(self._album_duration_label)

        self._list = QListWidget(self)
        self._list.setSelectionMode(QAbstractItemView.NoSelection)
        self._list.setFocusPolicy(Qt.NoFocus)
        self._list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.setStyleSheet(
            "QScrollBar:vertical {"
            "  background: transparent;"
            "  width: 6px;"
            "  margin: 0px;"
            "}"
            "QScrollBar::handle:vertical {"
            "  background: rgba(0, 0, 0, 0);"
            "  min-height: 24px;"
            "  border-radius: 3px;"
            "}"
            "QScrollBar::handle:vertical:hover {"
            "  background: rgba(120, 120, 120, 160);"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
            "  height: 0px;"
            "}"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
            "  background: transparent;"
            "}"
        )

        layout.addWidget(self._list)

        self._items = []
        self._default_font = self._list.font()
        self._highlight_font = self._list.font()
        self._highlight_font.setPointSize(self._default_font.pointSize() + 4)
        self._highlight_font.setBold(True)
        self._near_font = self._list.font()
        self._near_font.setPointSize(self._default_font.pointSize() + 2)
        self._current_index = -1
        self.set_cover(None)
        self.set_track_info("", "", "", None)
        self._update_list_height()

    def set_track_info(self, title: str, artist: str, album: str, duration_seconds: float | None):
        title_text = title or "-"
        artist_text = artist or "-"
        album_text = album or "-"
        duration_text = self._format_duration(duration_seconds)
        self._title_artist_label.setText(f"标题：{title_text}    艺术家：{artist_text}")
        self._album_duration_label.setText(f"专辑：{album_text}    时长：{duration_text}")

    def set_cover(self, pixmap: QPixmap | None):
        if pixmap is None or pixmap.isNull():
            default_path = Path(__file__).resolve().parent.parent / ".." / "assets" / "icons" / "application.png"
            pixmap = QPixmap(str(default_path))
            if pixmap.isNull():
                self._cover_label.clear()
                return

        scaled = pixmap.scaled(
            160,
            160,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._cover_label.setPixmap(scaled)

    def set_lines(self, lines: list[str]):
        self._list.clear()
        self._items = []
        self._current_index = -1
        for text in lines:
            item = QListWidgetItem(text)
            item.setFont(self._default_font)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self._list.addItem(item)
            self._items.append(item)
        if not lines:
            item = QListWidgetItem("暂无歌词")
            item.setFont(self._default_font)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self._list.addItem(item)
            self._items.append(item)
        self._update_list_height()

    def set_current_index(self, index: int):
        if index == self._current_index:
            return
        if 0 <= self._current_index < len(self._items):
            self._items[self._current_index].setFont(self._default_font)
        if 0 <= self._current_index - 1 < len(self._items):
            self._items[self._current_index - 1].setFont(self._default_font)
        if 0 <= self._current_index + 1 < len(self._items):
            self._items[self._current_index + 1].setFont(self._default_font)

        self._current_index = index
        if 0 <= self._current_index < len(self._items):
            item = self._items[self._current_index]
            item.setFont(self._highlight_font)
            if 0 <= self._current_index - 1 < len(self._items):
                self._items[self._current_index - 1].setFont(self._near_font)
            if 0 <= self._current_index + 1 < len(self._items):
                self._items[self._current_index + 1].setFont(self._near_font)
            self._list.scrollToItem(item, QAbstractItemView.PositionAtCenter)

    def _update_list_height(self):
        metrics = QFontMetrics(self._highlight_font)
        line_height = metrics.height()
        visible_lines = min(max(len(self._items), 1), 5)
        frame = self._list.frameWidth() * 2
        self._list.setFixedHeight(line_height * visible_lines + frame + 4)

    def _format_duration(self, duration_seconds: float | None) -> str:
        if duration_seconds is None:
            return "-"
        total = int(duration_seconds)
        minutes, seconds = divmod(total, 60)
        return f"{minutes:02d}:{seconds:02d}"
