from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QAbstractItemView,
    QMenu,
)


class LibraryView(QWidget):
    def __init__(self, parent, on_activate, on_remove=None):
        super().__init__(parent)
        self._on_activate = on_activate
        self._on_remove = on_remove

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tree = QTreeWidget(self)
        self._tree.setColumnCount(3)
        self._tree.setHeaderLabels(["标题", "艺术家", "专辑"])
        self._tree.setColumnWidth(0, 260)
        self._tree.setColumnWidth(1, 170)
        self._tree.setColumnWidth(2, 200)
        self._tree.setRootIsDecorated(False)
        self._tree.setAlternatingRowColors(True)
        self._tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.setStyleSheet(
            "QScrollBar:vertical {"
            "  background: transparent;"
            "  width: 6px;"
            "  margin: 0px;"
            "}"
            "QScrollBar::handle:vertical {"
            "  background: rgba(120, 120, 120, 160);"
            "  min-height: 24px;"
            "  border-radius: 3px;"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
            "  height: 0px;"
            "}"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
            "  background: transparent;"
            "}"
            "QScrollBar:horizontal {"
            "  background: transparent;"
            "  height: 6px;"
            "  margin: 0px;"
            "}"
            "QScrollBar::handle:horizontal {"
            "  background: rgba(120, 120, 120, 160);"
            "  min-width: 24px;"
            "  border-radius: 999px;"
            "}"
            "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {"
            "  width: 0px;"
            "}"
            "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {"
            "  background: transparent;"
            "}"
            "QTreeWidget {"
            "  background: #f7f7f7;"
            "  border: 1px solid rgba(0, 0, 0, 0.08);"
            "  border-radius: 6px;"
            "  padding: 4px;"
            "}"
            "QTreeWidget::item {"
            "  padding: 4px 6px;"
            "}"
            "QTreeWidget::item:alternate {"
            "  background: rgba(0, 0, 0, 0.02);"
            "}"
            "QTreeWidget::item:hover {"
            "  background: rgba(0, 0, 0, 0.04);"
            "}"
            "QTreeWidget::item:selected {"
            "  background: rgba(0, 0, 0, 0.08);"
            "}"
            "QHeaderView::section {"
            "  background: rgba(0, 0, 0, 0.03);"
            "  padding: 6px 6px;"
            "  border: none;"
            "  border-bottom: 1px solid rgba(0, 0, 0, 0.08);"
            "  font-weight: 600;"
            "}"
        )
        self._tree.itemDoubleClicked.connect(self._activate)
        self._tree.customContextMenuRequested.connect(self._open_context_menu)

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
                ]
            )
            item.setData(0, Qt.UserRole, row["path"])
            self._tree.addTopLevelItem(item)

    def _activate(self, item, _column):
        path = item.data(0, Qt.UserRole)
        if not path:
            return
        self._on_activate(path)

    def selected_paths(self) -> list[str]:
        paths = []
        for item in self._tree.selectedItems():
            path = item.data(0, Qt.UserRole)
            if path:
                paths.append(path)
        return paths

    def _open_context_menu(self, pos):
        if self._on_remove is None:
            return
        selected = self.selected_paths()
        if not selected:
            return
        menu = QMenu(self)
        remove_action = QAction("从库中移除", self)
        remove_action.triggered.connect(lambda: self._on_remove(selected))
        menu.addAction(remove_action)
        menu.exec(self._tree.viewport().mapToGlobal(pos))


def _format_duration(seconds: int) -> str:
    if not seconds:
        return ""
    m = seconds // 60
    s = seconds % 60
    return f"{m}:{s:02d}"
