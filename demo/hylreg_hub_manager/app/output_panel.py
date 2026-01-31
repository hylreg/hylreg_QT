"""显示 git 命令输出的只读文本框。"""

from PyQt6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class OutputPanel(QWidget):
    """底部输出面板：只读，显示最近执行的 git 命令及输出。"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._text = QPlainTextEdit(self)
        self._text.setReadOnly(True)
        self._text.setPlaceholderText("执行 git 命令后，输出将显示在这里…")
        font = QFont("Monospace", 10)
        self._text.setFont(font)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._text)

    def append_command(self, cmd: str) -> None:
        """追加一条命令（带前缀）。"""
        self._text.appendPlainText(f"$ {cmd}")
        self._text.ensureCursorVisible()

    def append_stdout(self, text: str) -> None:
        """追加标准输出。"""
        if text:
            self._text.appendPlainText(text.rstrip())
        self._text.ensureCursorVisible()

    def append_stderr(self, text: str) -> None:
        """追加标准错误（可高亮）。"""
        if text:
            self._text.appendPlainText(text.rstrip())
        self._text.ensureCursorVisible()

    def append_result(self, returncode: int) -> None:
        """追加返回码。"""
        self._text.appendPlainText(f"[exit {returncode}]")
        self._text.appendPlainText("")
        self._text.ensureCursorVisible()

    def clear(self) -> None:
        """清空输出。"""
        self._text.clear()
