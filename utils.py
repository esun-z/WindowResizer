import ctypes
import os
import win32gui
import win32process
import win32api
import win32con

def is_admin():
    """Check if the application is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def find_window_by_process(process_name):
    """Find a window handle by the process name."""
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
