"""子模块操作按钮与逻辑入口。"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QGroupBox,
    QInputDialog,
)
from PyQt6.QtCore import pyqtSignal


class SubmoduleActions(QWidget):
    """添加/初始化/更新/删除等按钮。"""

    add_submodule = pyqtSignal(str, str)  # url, path
    init_selected = pyqtSignal()
    init_all = pyqtSignal()
    update_to_record = pyqtSignal()
    update_to_remote = pyqtSignal()
    remove_selected = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        grp = QGroupBox("子模块操作")
        inner = QVBoxLayout(grp)

        row1 = QHBoxLayout()
        self._add_btn = QPushButton("添加子模块")
        self._add_btn.clicked.connect(self._on_add)
        self._init_all_btn = QPushButton("全部初始化")
        self._init_all_btn.clicked.connect(lambda: self.init_all.emit())
        self._init_sel_btn = QPushButton("初始化选中")
        self._init_sel_btn.clicked.connect(lambda: self.init_selected.emit())
        row1.addWidget(self._add_btn)
        row1.addWidget(self._init_all_btn)
        row1.addWidget(self._init_sel_btn)
        inner.addLayout(row1)

        row2 = QHBoxLayout()
        self._update_record_btn = QPushButton("更新到记录版本")
        self._update_record_btn.clicked.connect(lambda: self.update_to_record.emit())
        self._update_remote_btn = QPushButton("更新到远端最新")
        self._update_remote_btn.clicked.connect(lambda: self.update_to_remote.emit())
        self._remove_btn = QPushButton("删除选中")
        self._remove_btn.clicked.connect(lambda: self.remove_selected.emit())
        row2.addWidget(self._update_record_btn)
        row2.addWidget(self._update_remote_btn)
        row2.addWidget(self._remove_btn)
        inner.addLayout(row2)

        layout.addWidget(grp)

    def _on_add(self) -> None:
        url, ok = QInputDialog.getText(
            self,
            "添加子模块",
            "子模块 Git URL：",
        )
        if not ok or not url.strip():
            return
        name, ok = QInputDialog.getText(
            self,
            "添加子模块",
            "子模块名称（将添加到 repos/<名称>）：",
            text="my-project",
        )
        if not ok or not name.strip():
            return
        path = f"repos/{name.strip()}"
        self.add_submodule.emit(url.strip(), path)

