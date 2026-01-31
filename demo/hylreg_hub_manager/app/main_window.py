"""主窗口：菜单、工具栏、中心布局。"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter,
    QMessageBox,
    QFileDialog,
    QApplication,
    QStatusBar,
)
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QAction

from app.repo_selector import RepoSelector
from app.submodule_table import SubmoduleTable
from app.submodule_actions import SubmoduleActions
from app.output_panel import OutputPanel
from app.git_worker import GitWorkerThread
from core.git_runner import load_submodules


class MainWindow(QMainWindow):
    """主窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("hylreg_QT — Git 子模块管理")
        self.setMinimumSize(800, 500)
        self.resize(1000, 650)

        self._repo_path = ""
        self._worker_thread: QThread | None = None

        self._build_menubar()
        self._build_ui()
        self._connect_signals()
        self.statusBar().showMessage("请选择 hub 仓库根目录")

    def _build_menubar(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件(&F)")
        open_act = QAction("打开仓库(&O)...", self)
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self._on_open_repo)
        file_menu.addAction(open_act)
        refresh_act = QAction("刷新(&R)", self)
        refresh_act.setShortcut("F5")
        refresh_act.triggered.connect(self._on_refresh)
        file_menu.addAction(refresh_act)
        file_menu.addSeparator()
        exit_act = QAction("退出(&X)", self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(QApplication.quit)
        file_menu.addAction(exit_act)

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self._repo_selector = RepoSelector(self)
        layout.addWidget(self._repo_selector)

        self._actions = SubmoduleActions(self)
        layout.addWidget(self._actions)

        self._table = SubmoduleTable(self)
        self._output = OutputPanel(self)
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self._table)
        splitter.addWidget(self._output)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        layout.addWidget(splitter)

    def _connect_signals(self) -> None:
        self._repo_selector.path_changed.connect(self._on_repo_changed)
        self._actions.add_submodule.connect(self._on_add_submodule)
        self._actions.init_selected.connect(self._on_init_selected)
        self._actions.init_all.connect(self._on_init_all)
        self._actions.update_to_record.connect(self._on_update_to_record)
        self._actions.update_to_remote.connect(self._on_update_to_remote)
        self._actions.remove_selected.connect(self._on_remove_selected)

    def _on_open_repo(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "选择 hub 仓库根目录",
            self._repo_selector.path() or "",
        )
        if path:
            self._repo_selector.set_path(path)

    def _on_repo_changed(self, path: str) -> None:
        self._repo_path = path
        self._refresh_submodules()
        self.statusBar().showMessage(f"已打开: {path}")

    def _on_refresh(self) -> None:
        if self._repo_path:
            self._refresh_submodules()
            self.statusBar().showMessage("已刷新子模块列表")
        else:
            self.statusBar().showMessage("请先选择仓库")

    def _refresh_submodules(self) -> None:
        if not self._repo_path:
            self._table.set_submodules([])
            return
        items = load_submodules(self._repo_path)
        self._table.set_submodules(items)

    def _selected_paths(self) -> list[str]:
        return self._table.selected_paths()

    def _run_git_and_show(self, args: list[str], then_refresh: bool = True) -> None:
        if not self._repo_path:
            self.statusBar().showMessage("请先选择仓库")
            return
        cmd = "git " + " ".join(args)
        self._output.append_command(cmd)
        self._worker_thread = GitWorkerThread(self._repo_path, args)
        self._worker_thread.finished.connect(
            lambda s, e, c: self._on_git_finished(s, e, c, then_refresh)
        )
        self._worker_thread.start()

    def _on_git_finished(
        self,
        stdout: str,
        stderr: str,
        returncode: int,
        then_refresh: bool,
    ) -> None:
        if stdout:
            self._output.append_stdout(stdout)
        if stderr:
            self._output.append_stderr(stderr)
        self._output.append_result(returncode)
        if then_refresh:
            self._refresh_submodules()
        self._worker_thread = None
        self.statusBar().showMessage(
            "命令完成" if returncode == 0 else f"命令退出码: {returncode}"
        )

    def _on_add_submodule(self, url: str, path: str) -> None:
        self._run_git_and_show(["submodule", "add", url, path])

    def _on_init_selected(self) -> None:
        paths = self._selected_paths()
        if not paths:
            QMessageBox.information(self, "提示", "请先在表格中选中要初始化的子模块")
            return
        args = ["submodule", "update", "--init", "--recursive"] + paths
        self._run_git_and_show(args)

    def _on_init_all(self) -> None:
        self._run_git_and_show(["submodule", "update", "--init", "--recursive"])

    def _on_update_to_record(self) -> None:
        paths = self._selected_paths()
        if not paths:
            QMessageBox.information(self, "提示", "请先在表格中选中要更新的子模块")
            return
        args = ["submodule", "update", "--init", "--recursive"] + paths
        self._run_git_and_show(args)

    def _on_update_to_remote(self) -> None:
        paths = self._selected_paths()
        if not paths:
            QMessageBox.information(self, "提示", "请先在表格中选中要更新到远端的子模块")
            return
        for p in paths:
            self._run_git_and_show(["submodule", "update", "--remote", p])
        QMessageBox.information(
            self,
            "提示",
            "已更新到远端。若需在主仓库记录新 commit，请执行：\n"
            "git add <子模块路径>\n"
            "git commit -m \"chore: 更新子模块\"",
        )

    def _on_remove_selected(self) -> None:
        paths = self._selected_paths()
        if not paths:
            QMessageBox.information(self, "提示", "请先在表格中选中要删除的子模块")
            return
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除以下子模块吗？\n" + "\n".join(paths),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        for p in paths:
            self._run_git_and_show(["submodule", "deinit", "-f", p])
            self._run_git_and_show(["rm", "-f", p])
        self.statusBar().showMessage("删除后请提交主仓库变更")
