from PySide6.QtWidgets import (QMainWindow, QListWidgetItem, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor
import win32gui
import win32ui
import ctypes
from ui_main_window import Ui_main_window as ui
from utils import find_window_by_process
from presets import presets
from log_level import LogLevel

class MainWindow(QMainWindow, ui):

    MAX_LOGS = 1000

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.detect_button.clicked.connect(self.update_current_resolution)
        self.apply_button.clicked.connect(self.apply_resolution)
        self.screenshot_button.clicked.connect(self.take_screenshot)
        self.save_button.clicked.connect(self.save_screenshot)

        self.preset_combo.addItems(presets.keys())
        self.preset_combo.currentIndexChanged.connect(self.apply_preset)

        self.screenshot_pixmap = None

    def log(self, message, level=LogLevel.INFO):
        if self.log_list.count() >= self.MAX_LOGS:
            self.log_list.takeItem(0)

        log_message = f"[{level.name}] {message}"
        item = QListWidgetItem(log_message)
        # Use QColor with alpha for transparency (128 = 50%)
        if level == LogLevel.WARNING:
            item.setBackground(QColor(255, 255, 0, 128))  # yellow, 50% transparent
        elif level == LogLevel.ERROR:
            item.setBackground(QColor(255, 165, 0, 128))  # orange, 50% transparent

        self.log_list.addItem(item)
        self.log_list.scrollToBottom()

    def apply_preset(self):
        preset = self.preset_combo.currentText()
        if preset in presets:
            width, height = presets[preset]
            self.width_input.setText(str(width))
            self.height_input.setText(str(height))
            self.log(f"Applied preset: {preset} ({width}x{height})")
        else:
            self.log(f"Preset '{preset}' not found.", LogLevel.WARNING)

    def apply_resolution(self):
        title = self.title_input.text()
        process_name = self.process_input.text()
        width = self.width_input.text()
        height = self.height_input.text()

        if not width.isdigit() or not height.isdigit():
            self.log("Width and Height must be numeric values.", LogLevel.ERROR)
            return

        target_width, target_height = int(width), int(height)

        hwnd = None
        if title:
            hwnd = win32gui.FindWindow(None, title)
        if not hwnd and process_name:
            hwnd = find_window_by_process(process_name)

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
            self.log("Could not find the target window.", LogLevel.ERROR)

    def update_current_resolution(self):
        title = self.title_input.text()
        process_name = self.process_input.text()

        hwnd = None
        if title:
            hwnd = win32gui.FindWindow(None, title)
        if not hwnd and process_name:
            hwnd = find_window_by_process(process_name)

        if hwnd:
            rect = win32gui.GetClientRect(hwnd)
            self.current_resolution_label.setText(f"Current Resolution: {rect[2] - rect[0]}x{rect[3] - rect[1]}")
            self.log(f"Current resolution: {rect[2] - rect[0]}x{rect[3] - rect[1]}")
        else:
            self.current_resolution_label.setText("Current Resolution: N/A")
            self.log("Could not find the target window.", LogLevel.WARNING)

    def take_screenshot(self):
        title = self.title_input.text()
        process_name = self.process_input.text()

        hwnd = None
        if title:
            hwnd = win32gui.FindWindow(None, title)
        if not hwnd and process_name:
            hwnd = find_window_by_process(process_name)

        if not hwnd:
            self.log("Could not find the target window for screenshot.", LogLevel.ERROR)
            return

        # Get client area size
        client_rect = win32gui.GetClientRect(hwnd)
        width = client_rect[2] - client_rect[0]
        height = client_rect[3] - client_rect[1]

        if width <= 0 or height <= 0:
            self.log("Client area has zero size.", LogLevel.ERROR)
            return

        try:
            # Create a compatible DC (with screen, not window!)
            screen_dc = win32gui.GetDC(0)  # Screen DC
            mem_dc = win32ui.CreateDCFromHandle(screen_dc)
            compatible_dc = mem_dc.CreateCompatibleDC()

            # Create compatible bitmap
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mem_dc, width, height)
            compatible_dc.SelectObject(bitmap)

            # Use PrintWindow to render client area into memory DC
            # PW_CLIENTONLY = 1 | PW_RENDERFULLCONTENT = 2 => 3
            result = ctypes.windll.user32.PrintWindow(hwnd, compatible_dc.GetSafeHdc(), 3)

            if not result:
                self.log("PrintWindow failed to capture the client area.", LogLevel.ERROR)
                return

            # Save to file
            bitmap.SaveBitmapFile(compatible_dc, "screenshot.bmp")

            # Load into QLabel
            self.screenshot_pixmap = QPixmap("screenshot.bmp")
            self.screenshot_label.setPixmap(
                self.screenshot_pixmap.scaled(
                    self.screenshot_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

            self.log("Screenshot taken successfully.")

        finally:
            # Cleanup resources
            win32gui.DeleteObject(bitmap.GetHandle())
            compatible_dc.DeleteDC()
            mem_dc.DeleteDC()
            win32gui.ReleaseDC(0, screen_dc)

    def save_screenshot(self):
        if self.screenshot_pixmap:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "", "Images (*.png *.xpm *.jpg *.bmp)")
            if file_path:
                self.screenshot_pixmap.save(file_path)
                self.log(f"Screenshot saved to {file_path}.")
        else:
            self.log("No screenshot available to save.", LogLevel.WARNING)

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())