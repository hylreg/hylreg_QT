"""选择/打开 hub 仓库。"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
)
from PyQt6.QtCore import pyqtSignal


class RepoSelector(QWidget):
    """当前仓库路径：只读输入框 + 浏览按钮。"""

    path_changed = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._path_edit = QLineEdit(self)
        self._path_edit.setReadOnly(True)
        self._path_edit.setPlaceholderText("请选择 hub 仓库根目录…")
        self._browse_btn = QPushButton("浏览…", self)
        self._browse_btn.clicked.connect(self._on_browse)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._path_edit)
        layout.addWidget(self._browse_btn)

    def _on_browse(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "选择 hub 仓库根目录",
            self._path_edit.text() or str(Path.home()),
        )
        if path:
            self.set_path(path)

    def set_path(self, path: str) -> None:
        """设置并校验路径（需存在 .git）。"""
        p = Path(path)
        if not p.is_dir():
            return
        if not (p / ".git").exists():
            return
        self._path_edit.setText(path)
        self.path_changed.emit(path)

    def path(self) -> str:
        """当前选中的路径。"""
        return self._path_edit.text().strip()

    def clear(self) -> None:
        """清空路径。"""
        self._path_edit.clear()
