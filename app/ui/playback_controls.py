from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QSlider, QLabel, QHBoxLayout


class PlaybackControls(QWidget):
    def __init__(self, parent, on_play, on_pause, on_stop, on_seek):
        super().__init__(parent)
        self._on_play = on_play
        self._on_pause = on_pause
        self._on_stop = on_stop
        self._on_seek = on_seek

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        play_button = QPushButton("播放", self)
        pause_button = QPushButton("暂停", self)
        stop_button = QPushButton("停止", self)

        play_button.clicked.connect(self._on_play)
        pause_button.clicked.connect(self._on_pause)
        stop_button.clicked.connect(self._on_stop)

        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setRange(0, 100)
        self._slider.setSingleStep(1)
        self._slider.setPageStep(5)
        self._slider.valueChanged.connect(self._seek)

        self._time = QLabel("00:00 / 00:00", self)
        self._time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(play_button)
        layout.addWidget(pause_button)
        layout.addWidget(stop_button)
        layout.addWidget(self._slider, 1)
        layout.addWidget(self._time)

    def _seek(self, value: int):
        fraction = float(value) / 100.0
        self._on_seek(fraction)

    def set_position(self, fraction: float, current: float, total: float) -> None:
        value = int(fraction * 100)
        was_blocked = self._slider.blockSignals(True)
        self._slider.setValue(value)
        self._slider.blockSignals(was_blocked)
        self._time.setText(f"{_fmt(current)} / {_fmt(total)}")


def _fmt(seconds: float) -> str:
    s = int(seconds or 0)
    m = s // 60
    s = s % 60
    return f"{m:02d}:{s:02d}"
