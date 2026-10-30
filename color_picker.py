import ctypes
from ctypes import wintypes

# Windows API constants
SRCCOPY = 0x00CC0020

# Load Windows DLLs
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


def get_cursor_pos() -> tuple[int, int]:
    """Get current mouse cursor position."""
    point = POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y


def get_pixel_color(x: int, y: int) -> tuple[int, int, int]:
    """Get RGB color of pixel at screen coordinates (x, y)."""
    hdc = user32.GetDC(None)
    color = gdi32.GetPixel(hdc, x, y)
    user32.ReleaseDC(None, hdc)

    # GetPixel failure returns CLR_INVALID (-1); raise so callers keep the
    # last color instead of decoding the failure value as white.
    if color == -1:
        raise ValueError("GetPixel failed")

    # Windows returns BGR format (0x00BBGGRR)
    r = color & 0xFF
    g = (color >> 8) & 0xFF
    b = (color >> 16) & 0xFF
    return r, g, b


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to HEX string."""
    return f"#{r:02X}{g:02X}{b:02X}"
