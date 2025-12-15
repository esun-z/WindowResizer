import sys
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QComboBox, QMessageBox)
from PySide6.QtCore import Qt, QEvent
import win32gui
import win32process
import win32con
import os
import win32api

class WindowResizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window Resizer")
        self.setGeometry(100, 100, 400, 300)

        # Main layout
        layout = QVBoxLayout()

        # Input fields for title and process name
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Enter Window Title")
        self.title_input.editingFinished.connect(self.update_current_resolution)
        layout.addWidget(self.title_input)

        self.process_input = QLineEdit(self)
        self.process_input.setPlaceholderText("Enter Process Name")
        self.process_input.editingFinished.connect(self.update_current_resolution)
        layout.addWidget(self.process_input)

        # Label to show current resolution
        self.current_resolution_label = QLabel("Current Resolution: N/A", self)
        layout.addWidget(self.current_resolution_label)

        # Input fields for target resolution
        self.width_input = QLineEdit(self)
        self.width_input.setPlaceholderText("Width")
        layout.addWidget(self.width_input)

        self.height_input = QLineEdit(self)
        self.height_input.setPlaceholderText("Height")
        layout.addWidget(self.height_input)

        # Preset resolutions
        self.preset_combo = QComboBox(self)
        self.preset_combo.addItems([
            "Select Preset",
            "4:3 - 720p",
            "4:3 - 1080p",
            "4:3 - 1440p",
            "4:3 - 2160p",
            "16:9 - 720p",
            "16:9 - 1080p",
            "16:9 - 1440p",
            "16:9 - 2160p",
            "21:9 - 720p",
            "21:9 - 1080p",
            "21:9 - 1440p",
            "21:9 - 2160p",
        ])
        self.preset_combo.currentIndexChanged.connect(self.apply_preset)
        layout.addWidget(self.preset_combo)

        # Apply button
        self.apply_button = QPushButton("Apply Resolution", self)
        self.apply_button.clicked.connect(self.apply_resolution)
        layout.addWidget(self.apply_button)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def apply_preset(self):
        presets = {
            "4:3 - 720p": (960, 720),
            "4:3 - 1080p": (1440, 1080),
            "4:3 - 1440p": (1920, 1440),
            "4:3 - 2160p": (2880, 2160),
            "16:9 - 720p": (1280, 720),
            "16:9 - 1080p": (1920, 1080),
            "16:9 - 1440p": (2560, 1440),
            "16:9 - 2160p": (3840, 2160),
            "21:9 - 720p": (1680, 720),
            "21:9 - 1080p": (2560, 1080),
            "21:9 - 1440p": (3360, 1440),
            "21:9 - 2160p": (5040, 2160),
        }
        preset = self.preset_combo.currentText()
        if preset in presets:
            width, height = presets[preset]
            self.width_input.setText(str(width))
            self.height_input.setText(str(height))

    def apply_resolution(self):
        title = self.title_input.text()
        process_name = self.process_input.text()
        width = self.width_input.text()
        height = self.height_input.text()

        if not width.isdigit() or not height.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Width and Height must be integers.")
            return

        target_width, target_height = int(width), int(height)

        hwnd = None
        if title:
            hwnd = win32gui.FindWindow(None, title)
        if not hwnd and process_name:
            hwnd = self.find_window_by_process(process_name)

        if hwnd:
            # Get current window and client area dimensions
            rect = win32gui.GetWindowRect(hwnd)
            client_rect = win32gui.GetClientRect(hwnd)

            outer_width = rect[2] - rect[0]
            outer_height = rect[3] - rect[1]
            client_width = client_rect[2] - client_rect[0]
            client_height = client_rect[3] - client_rect[1]

            # Calculate border and title bar sizes
            border_width = (outer_width - client_width) // 2
            title_bar_height = outer_height - client_height - border_width

            # Calculate new outer dimensions
            new_width = target_width + 2 * border_width
            new_height = target_height + title_bar_height + border_width

            # Move and resize the window
            win32gui.MoveWindow(hwnd, rect[0], rect[1], new_width, new_height, True)
            self.update_current_resolution()
        else:
            QMessageBox.warning(self, "Window Not Found", "Could not find the target window.")

    def find_window_by_process(self, process_name):
        def callback(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd):
                return

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                handle = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid
                )
                exe_path = win32process.GetModuleFileNameEx(handle, 0)
                exe_name = os.path.basename(exe_path).lower()
                if process_name.lower() == exe_name:
                    extra.append(hwnd)
            except Exception as e:
                print(f"Error accessing process {pid}: {e}")

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds[0] if hwnds else None

    def update_current_resolution(self):
        title = self.title_input.text()
        process_name = self.process_input.text()

        hwnd = None
        if title:
            hwnd = win32gui.FindWindow(None, title)
        if not hwnd and process_name:
            hwnd = self.find_window_by_process(process_name)

        if hwnd:
            rect = win32gui.GetClientRect(hwnd)
            self.current_resolution_label.setText(f"Current Resolution: {rect[2] - rect[0]}x{rect[3] - rect[1]}")
        else:
            self.current_resolution_label.setText("Current Resolution: N/A")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def main():
    # Check if the application is running as an administrator
    if not is_admin():
        # Relaunch the application with elevated privileges
        params = " ".join(sys.argv)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit(0)  # Exit the current process

    # Continue with the application if already running as admin
    app = QApplication(sys.argv)
    window = WindowResizer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()