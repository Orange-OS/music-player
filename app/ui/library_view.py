from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout


class LibraryView(QWidget):
    def __init__(self, parent, on_activate):
        super().__init__(parent)
        self._on_activate = on_activate

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tree = QTreeWidget(self)
        self._tree.setColumnCount(4)
        self._tree.setHeaderLabels(["标题", "艺术家", "专辑", "时长"])
        self._tree.setColumnWidth(0, 220)
        self._tree.setColumnWidth(1, 140)
        self._tree.setColumnWidth(2, 140)
        self._tree.setColumnWidth(3, 60)
        self._tree.setRootIsDecorated(False)
        self._tree.setAlternatingRowColors(True)
        self._tree.itemDoubleClicked.connect(self._activate)

        layout.addWidget(self._tree)

    def activate_relative(self, offset: int):
        count = self._tree.topLevelItemCount()
        if count == 0:
            return
        current = self._tree.currentItem()
        if current is None:
            index = 0
        else:
            index = self._tree.indexOfTopLevelItem(current)
            if index < 0:
                index = 0
        new_index = max(0, min(count - 1, index + offset))
        item = self._tree.topLevelItem(new_index)
        if item is None:
            return
        self._tree.setCurrentItem(item)
        self._activate(item, 0)

    def activate_next(self):
        self.activate_relative(1)

    def activate_previous(self):
        self.activate_relative(-1)

    def set_tracks(self, rows):
        self._tree.clear()
        for row in rows:
            item = QTreeWidgetItem(
                [
                    row["title"],
                    row["artist"],
                    row["album"],
                    _format_duration(row["duration"]),
                ]
            )
            item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
            item.setData(0, Qt.UserRole, row["path"])
            self._tree.addTopLevelItem(item)

    def _activate(self, item, _column):
        path = item.data(0, Qt.UserRole)
        if not path:
            return
        self._on_activate(path)


def _format_duration(seconds: int) -> str:
    if not seconds:
        return ""
    m = seconds // 60
    s = seconds % 60
    return f"{m}:{s:02d}"
