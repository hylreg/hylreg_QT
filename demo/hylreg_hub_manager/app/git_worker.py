"""在后台线程执行 git 命令，通过信号返回结果。"""

from PyQt6.QtCore import QObject, QThread, pyqtSignal


class GitWorker(QObject):
    """在后台线程执行 git 命令。"""

    finished = pyqtSignal(str, str, int)  # stdout, stderr, returncode
    output_line = pyqtSignal(str)  # 逐行输出（可选）

    def __init__(self, repo_root: str, args: list[str], timeout: int = 120):
        super().__init__()
        self.repo_root = repo_root
        self.args = args
        self.timeout = timeout
        self._cancel = False

    def run(self) -> None:
        import subprocess
        try:
            proc = subprocess.Popen(
                ["git", *self.args],
                cwd=self.repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = proc.communicate(timeout=self.timeout)
            code = proc.returncode or 0
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            stdout, stderr, code = "", str(e), -1
        self.finished.emit(stdout or "", stderr or "", code)

    def cancel(self) -> None:
        self._cancel = True


class GitWorkerThread(QThread):
    """包装 GitWorker 的 QThread。"""

    finished = pyqtSignal(str, str, int)

    def __init__(self, repo_root: str, args: list[str], timeout: int = 120):
        super().__init__()
        self.repo_root = repo_root
        self.args = args
        self.timeout = timeout

    def run(self) -> None:
        from core.git_runner import run_git
        stdout, stderr, code = run_git(
            self.repo_root,
            self.args,
            timeout=self.timeout,
        )
        self.finished.emit(stdout, stderr, code)
