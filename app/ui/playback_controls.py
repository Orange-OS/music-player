from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QPushButton, QSlider, QLabel, QHBoxLayout


class JumpSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.position().x() if hasattr(event, "position") else event.x()
            value = QSlider.minimum(self) + ((QSlider.maximum(self) - QSlider.minimum(self)) * pos) / max(1, self.width())
            self.setValue(int(value))
            event.accept()
        super().mousePressEvent(event)


class PlaybackControls(QWidget):
    def __init__(self, parent, on_toggle, on_stop, on_seek, on_volume):
        super().__init__(parent)
        self._on_toggle = on_toggle
        self._on_stop = on_stop
        self._on_seek = on_seek
        self._on_volume = on_volume

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._toggle_button = QPushButton(self)
        self._toggle_button.setIcon(self._icon_for_state(False))
        self._toggle_button.setIconSize(QSize(24, 24))
        self._toggle_button.setFixedSize(32, 32)
        self._toggle_button.setToolTip("播放")
        self._toggle_button.setFlat(True)
        self._toggle_button.setStyleSheet(
            "QPushButton {"
            "  border: 1px solid rgba(0, 0, 0, 0.12);"
            "  border-radius: 6px;"
            "  background: #f7f7f7;"
            "}"
            "QPushButton:hover {"
            "  background: #f1f1f1;"
            "}"
        )
        stop_button = QPushButton("停止", self)
        stop_button.setFlat(True)
        stop_button.setStyleSheet(
            "QPushButton {"
            "  border: 1px solid rgba(0, 0, 0, 0.12);"
            "  border-radius: 6px;"
            "  padding: 4px 10px;"
            "  background: #f7f7f7;"
            "}"
            "QPushButton:hover {"
            "  background: #f1f1f1;"
            "}"
        )

        self._toggle_button.clicked.connect(self._on_toggle)
        stop_button.clicked.connect(self._on_stop)

        self._volume = JumpSlider(Qt.Horizontal, self)
        self._volume.setRange(0, 100)
        self._volume.setSingleStep(1)
        self._volume.setPageStep(5)
        self._volume.setFixedWidth(110)
        self._volume.setStyleSheet(
            "QSlider::groove:horizontal {"
            "  height: 6px;"
            "  background: #e2e2e2;"
            "  border-radius: 3px;"
            "}"
            "QSlider::sub-page:horizontal {"
            "  background: #c5c5c5;"
            "  border-radius: 3px;"
            "}"
            "QSlider::handle:horizontal {"
            "  width: 12px;"
            "  margin: -3px 0;"
            "  border-radius: 6px;"
            "  background: #8c8c8c;"
            "}"
            "QSlider::handle:horizontal:hover {"
            "  background: #6f6f6f;"
            "}"
        )
        self._volume.valueChanged.connect(self._on_volume)

        self._slider = JumpSlider(Qt.Horizontal, self)
        self._slider.setRange(0, 100)
        self._slider.setSingleStep(1)
        self._slider.setPageStep(5)
        self._slider.setStyleSheet(
            "QSlider::groove:horizontal {"
            "  height: 6px;"
            "  background: #e2e2e2;"
            "  border-radius: 3px;"
            "}"
            "QSlider::sub-page:horizontal {"
            "  background: #bdbdbd;"
            "  border-radius: 3px;"
            "}"
            "QSlider::handle:horizontal {"
            "  width: 12px;"
            "  margin: -3px 0;"
            "  border-radius: 6px;"
            "  background: #8c8c8c;"
            "}"
            "QSlider::handle:horizontal:hover {"
            "  background: #6f6f6f;"
            "}"
        )
        self._slider.valueChanged.connect(self._seek)

        self._time = QLabel("00:00 / 00:00", self)
        self._time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._time.setStyleSheet("color: rgba(0, 0, 0, 0.7);")

        layout.addWidget(self._toggle_button)
        layout.addWidget(stop_button)
        layout.addWidget(self._volume)
        layout.addWidget(self._slider, 1)
        layout.addWidget(self._time)

    def _seek(self, value: int):
        fraction = float(value) / 100.0
        self._on_seek(fraction)

    def set_is_playing(self, is_playing: bool) -> None:
        self._toggle_button.setIcon(self._icon_for_state(is_playing))
        self._toggle_button.setToolTip("暂停" if is_playing else "播放")

    def _icon_for_state(self, is_playing: bool) -> QIcon:
        base = Path(__file__).resolve().parent.parent / ".." / "assets" / "icons"
        icon_path = base / ("pause-icon.png" if is_playing else "play-button-icon.png")
        return QIcon(str(icon_path))

    def set_position(self, fraction: float, current: float, total: float) -> None:
        value = int(fraction * 100)
        was_blocked = self._slider.blockSignals(True)
        self._slider.setValue(value)
        self._slider.blockSignals(was_blocked)
        self._time.setText(f"{_fmt(current)} / {_fmt(total)}")

    def set_volume(self, value: int) -> None:
        volume = max(0, min(100, int(value)))
        was_blocked = self._volume.blockSignals(True)
        self._volume.setValue(volume)
        self._volume.blockSignals(was_blocked)


def _fmt(seconds: float) -> str:
    s = int(seconds or 0)
    m = s // 60
    s = s % 60
    return f"{m:02d}:{s:02d}"
