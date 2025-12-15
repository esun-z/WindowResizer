from PySide6.QtWidgets import (QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QComboBox, QMessageBox, QHBoxLayout, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import win32gui
import win32ui
import ctypes
from ui_main_window import Ui_main_window as ui
from utils import find_window_by_process
from presets import presets

class MainWindow(QMainWindow, ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.setWindowTitle("Window Resizer")
        # self.setGeometry(100, 100, 600, 400)  # Adjusted width for screenshot preview

        # # Main layout
        # layout = QVBoxLayout()

        # # Input fields for title and process name
        # input_layout = QVBoxLayout()

        # self.title_input = QLineEdit(self)
        # self.title_input.setPlaceholderText("Enter Window Title")
        # input_layout.addWidget(self.title_input)

        # self.process_input = QLineEdit(self)
        # self.process_input.setPlaceholderText("Enter Process Name")
        # input_layout.addWidget(self.process_input)

        # layout.addLayout(input_layout)

        # # Single Detect button
        # self.detect_button = QPushButton("Detect", self)
        self.detect_button.clicked.connect(self.update_current_resolution)
        # layout.addWidget(self.detect_button)

        # # Label to show current resolution
        # self.current_resolution_label = QLabel("Current Resolution: N/A", self)
        # layout.addWidget(self.current_resolution_label)

        # # Screenshot preview and buttons
        # self.screenshot_label = QLabel("Screenshot Preview", self)
        # self.screenshot_label.setFixedSize(200, 150)
        # layout.addWidget(self.screenshot_label)

        # screenshot_buttons_layout = QHBoxLayout()
        # self.screenshot_button = QPushButton("Take Screenshot", self)
        self.screenshot_button.clicked.connect(self.take_screenshot)
        # screenshot_buttons_layout.addWidget(self.screenshot_button)

        # self.save_button = QPushButton("Save As...", self)
        self.save_button.clicked.connect(self.save_screenshot)
        # screenshot_buttons_layout.addWidget(self.save_button)

        # layout.addLayout(screenshot_buttons_layout)

        # # Input fields for target resolution
        # self.width_input = QLineEdit(self)
        # self.width_input.setPlaceholderText("Width")
        # layout.addWidget(self.width_input)

        # self.height_input = QLineEdit(self)
        # self.height_input.setPlaceholderText("Height")
        # layout.addWidget(self.height_input)

        # # Preset resolutions
        # self.preset_combo = QComboBox(self)
        self.preset_combo.addItems(presets.keys())
        self.preset_combo.currentIndexChanged.connect(self.apply_preset)
        # layout.addWidget(self.preset_combo)

        # # Apply button
        # self.apply_button = QPushButton("Apply Resolution", self)
        self.apply_button.clicked.connect(self.apply_resolution)
        # layout.addWidget(self.apply_button)

        # # Set central widget
        # central_widget = QWidget()
        # central_widget.setLayout(layout)
        # self.setCentralWidget(central_widget)

        # Placeholder for screenshot pixmap
        self.screenshot_pixmap = None

    def apply_preset(self):
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
            QMessageBox.warning(self, "Window Not Found", "Could not find the target window.")

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
        else:
            self.current_resolution_label.setText("Current Resolution: N/A")

    def take_screenshot(self):
        title = self.title_input.text()
        process_name = self.process_input.text()

        hwnd = None
        if title:
            hwnd = win32gui.FindWindow(None, title)
        if not hwnd and process_name:
            hwnd = find_window_by_process(process_name)

        if not hwnd:
            QMessageBox.warning(self, "Window Not Found", "Could not find the target window.")
            return

        # Get client area size
        client_rect = win32gui.GetClientRect(hwnd)
        width = client_rect[2] - client_rect[0]
        height = client_rect[3] - client_rect[1]

        if width <= 0 or height <= 0:
            QMessageBox.warning(self, "Invalid Window", "Client area has zero size.")
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
                QMessageBox.warning(self, "Screenshot Failed", "PrintWindow failed to capture the client area.")
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
        else:
            QMessageBox.warning(self, "No Screenshot", "No screenshot available to save.")

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())