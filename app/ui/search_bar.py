from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout


class SearchBar(QWidget):
    def __init__(self, parent, on_search):
        super().__init__(parent)
        self._on_search = on_search

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("搜索", self)
        self._entry = QLineEdit(self)

        layout.addWidget(label)
        layout.addWidget(self._entry, 1)

        self._entry.textChanged.connect(self._handle)

    def _handle(self, text: str):
        self._on_search(text)
