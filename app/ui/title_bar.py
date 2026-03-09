from pathlib import Path

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(6)

        icon_label = QLabel(self)
        icon_label.setFixedSize(24, 24)
        icon_path = Path(__file__).resolve().parent.parent / ".." / "assets" / "icons" / "application.png"
        icon = QIcon(str(icon_path))
        icon_label.setPixmap(icon.pixmap(22, 22))
        layout.addWidget(icon_label)

        title = QLabel(self)
        title.setText(self.window().windowTitle())
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(title)

        self._min_button = QPushButton("—", self)
        self._close_button = QPushButton("×", self)

        self._min_button.clicked.connect(self._on_minimize)
        self._close_button.clicked.connect(self._on_close)

        for button in (self._min_button, self._close_button):
            button.setFixedSize(32, 24)
            button.setCursor(Qt.PointingHandCursor)
            layout.addWidget(button)

        self.setStyleSheet(
            "QWidget {"
            "  background: #f3f3f3;"
            "  border-top-left-radius: 8px;"
            "  border-top-right-radius: 8px;"
            "}"
            "QLabel {"
            "  color: #2b2b2b;"
            "  background: transparent;"
            "  border: none;"
            "}"
            "QPushButton {"
            "  background: transparent;"
            "  border: none;"
            "  border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "  background: rgba(0, 0, 0, 0.08);"
            "}"
            "QPushButton:pressed {"
            "  background: rgba(0, 0, 0, 0.14);"
            "}"
        )

    def _on_minimize(self):
        window = self.window()
        if window is not None:
            window.showMinimized()

    def _on_close(self):
        window = self.window()
        if window is not None:
            window.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            window = self.window()
            if window is not None and not window.isMaximized():
                window.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()
            else:
                super().mouseMoveEvent(event)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
        super().mouseReleaseEvent(event)
