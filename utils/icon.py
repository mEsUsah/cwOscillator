import os
import sys
import ctypes
import ctypes.wintypes as wintypes


def resource_path(rel: str) -> str:
    """Resolve a resource path for both dev and PyInstaller builds."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__ + "/..")))
    return os.path.join(base, rel)


def set_icon(window, ico_path: str):
    """Set window + taskbar icon using PIL iconphoto + ctypes class override."""
    from PIL import Image, ImageTk

    window.update_idletasks()

    # PIL iconphoto — sets title bar icon
    img = Image.open(ico_path).convert("RGBA")
    photo = ImageTk.PhotoImage(img)
    window.iconphoto(True, photo)
    window._icon_photo = photo  # prevent garbage collection

    # ctypes — override window class icon so taskbar picks it up
    hwnd = window.winfo_id()
    user32 = ctypes.windll.user32
    buf_l = (wintypes.HICON * 1)()
    buf_s = (wintypes.HICON * 1)()
    if ctypes.windll.shell32.ExtractIconExW(sys.executable, 0, buf_l, buf_s, 1) > 0:
        if buf_l[0]:
            user32.SetClassLongPtrW(hwnd, -14, buf_l[0])   # GCL_HICON
            user32.SendMessageW(hwnd, 0x80, 1, buf_l[0])   # WM_SETICON ICON_BIG
        if buf_s[0]:
            user32.SetClassLongPtrW(hwnd, -34, buf_s[0])   # GCL_HICONSM
            user32.SendMessageW(hwnd, 0x80, 0, buf_s[0])   # WM_SETICON ICON_SMALL
