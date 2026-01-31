"""hylreg_QT 入口：启动 QApplication 与主窗口。"""

import sys
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("hylreg_QT")
    app.setOrganizationName("hylreg")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
