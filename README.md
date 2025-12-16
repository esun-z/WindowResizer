# Window Resizer

## Overview
Window Resizer is a Python-based desktop application that allows users to detect, modify, and manage the resolution of application windows on Windows platforms. It is built using the PySide6 framework for the graphical user interface and provides features such as preset resolutions and screenshot capture.

## Features
- **Detect Current Resolution**: Identify the current resolution of a target window.
- **Apply Custom Resolutions**: Set custom width and height for application windows.
- **Preset Resolutions**: Choose from predefined resolution presets (e.g., 16:9, 4:3, 21:9 aspect ratios).
- **Take Screenshots**: Capture the client area of a target window and preview it within the application.
- **Save Screenshots**: Save captured screenshots in various image formats.
- **Logging**: View logs for actions performed.

## Installation

1. Clone the repository or download the source code.
2. Sync dependencies using uv:
   ```bash
   uv sync
   ```
3. Compile UI forms and translations
   ```bash
   uv run prebuild.py
   ```
4. Run the application
   ```bash
   uv run main.py
   ```

There are also pre-built executables available in [Release](https://github.com/esun-z/WindowResizer/releases).

## Usage

Use the graphical interface to:
- Detect the resolution of a window by entering its title or process name.
- Apply a custom resolution or select a preset.
- Take and save screenshots of the client area of a window.

## Project Structure
- `main.py`: Entry point of the application.
- `main_window.py`: Contains the main application logic and GUI interactions.
- `presets.py`: Stores predefined resolution presets.
- `utils.py`: Utility functions, including administrative privilege checks and resource path handling.
- `i18n/`: Contains translation files for localization (e.g., `zh_CN.qm`).
- `build/` and `dist/`: Directory for build artifacts (e.g., `.exe` files).

## Dependencies
- **PySide6**: For creating the graphical user interface.
- **pywin32**: For interacting with Windows APIs.
- **ctypes**: For low-level Windows operations.

## Localization
The application supports localization. Currently, a Chinese translation (`zh_CN.qm`) is included. The application automatically loads the appropriate translation based on the system locale.

## Building Executables
To create a standalone executable, use PyInstaller:
```bash
pyinstaller WindowResizer.spec
```
The executable will be available in the `dist/WindowResizer/` directory.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing
Contributions are welcome! Feel free to submit issues or pull requests to improve the project.