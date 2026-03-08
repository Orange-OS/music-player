from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class LyricsView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel("", self)
        self._label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._label.setWordWrap(True)

        layout.addWidget(self._label)

    def set_line(self, text: str):
        self._label.setText(text)
