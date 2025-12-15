from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from utils import is_admin
import sys
import ctypes

def main():
    # Check if the application is running as an administrator
    if not is_admin():
        # Relaunch the application with elevated privileges
        params = " ".join(sys.argv)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit(0)  # Exit the current process

    # Continue with the application if already running as admin
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()