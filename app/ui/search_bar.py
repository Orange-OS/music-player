from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QToolButton


class SearchBar(QWidget):
    def __init__(self, parent, on_search):
        super().__init__(parent)
        self._on_search = on_search

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._entry = QLineEdit(self)
        self._entry.setPlaceholderText("搜索标题/艺术家/专辑/路径")
        self._entry.setStyleSheet(
            "QLineEdit {"
            "  background: #f7f7f7;"
            "  border: 1px solid rgba(0, 0, 0, 0.12);"
            "  border-radius: 6px;"
            "  padding: 6px 8px;"
            "}"
            "QLineEdit:focus {"
            "  border: 1px solid rgba(0, 0, 0, 0.22);"
            "  background: #fafafa;"
            "}"
        )

        self._button = QToolButton(self)
        self._button.setToolTip("搜索")
        self._button.setIcon(self._search_icon())
        self._button.setAutoRaise(True)
        self._button.setStyleSheet(
            "QToolButton {"
            "  border: 1px solid rgba(0, 0, 0, 0.12);"
            "  border-radius: 6px;"
            "  padding: 4px;"
            "  background: #f7f7f7;"
            "}"
            "QToolButton:hover {"
            "  background: #f1f1f1;"
            "}"
        )
        self._button.clicked.connect(self._trigger_search)

        layout.addWidget(self._entry, 1)
        layout.addWidget(self._button)

        self._entry.textChanged.connect(self._handle)

    def _handle(self, text: str):
        self._on_search(text)

    def _trigger_search(self):
        self._on_search(self._entry.text())

    def _search_icon(self) -> QIcon:
        base = Path(__file__).resolve().parent.parent / ".." / "assets" / "icons"
        return QIcon(str(base / "search_icon.png"))
