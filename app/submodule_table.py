"""子模块列表表格。"""

from PyQt6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt

from core.models import SubmoduleInfo


class SubmoduleTable(QTableWidget):
    """子模块列表：路径、URL、commit、状态。"""

    COL_PATH = 0
    COL_URL = 1
    COL_COMMIT = 2
    COL_STATUS = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["路径", "URL", "Commit", "状态"])
        self.horizontalHeader().setSectionResizeMode(
            SubmoduleTable.COL_PATH,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.horizontalHeader().setSectionResizeMode(
            SubmoduleTable.COL_URL,
            QHeaderView.ResizeMode.Stretch,
        )
        self.horizontalHeader().setSectionResizeMode(
            SubmoduleTable.COL_COMMIT,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.horizontalHeader().setSectionResizeMode(
            SubmoduleTable.COL_STATUS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setAlternatingRowColors(True)

    def set_submodules(self, items: list[SubmoduleInfo]) -> None:
        """用子模块列表刷新表格。"""
        self.setRowCount(len(items))
        for row, info in enumerate(items):
            self.setItem(row, SubmoduleTable.COL_PATH, QTableWidgetItem(info.path))
            self.setItem(row, SubmoduleTable.COL_URL, QTableWidgetItem(info.url))
            self.setItem(row, SubmoduleTable.COL_COMMIT, QTableWidgetItem(info.commit))
            self.setItem(
                row,
                SubmoduleTable.COL_STATUS,
                QTableWidgetItem(info.status_display()),
            )
        if items:
            self.resizeRowsToContents()

    def selected_paths(self) -> list[str]:
        """返回当前选中的行对应的路径列表。"""
        paths: list[str] = []
        for idx in self.selectionModel().selectedRows():
            row = idx.row()
            path_item = self.item(row, SubmoduleTable.COL_PATH)
            if path_item:
                paths.append(path_item.text())
        return paths
