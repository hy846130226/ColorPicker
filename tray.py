from __future__ import annotations

from typing import TYPE_CHECKING

import pystray
from PIL import Image

from config import resource_path

if TYPE_CHECKING:
    from ui import ColorPickerApp

_ICON_NAME = "icons8-color-picker-48.ico"
_ICON_SIZE = 32


def _load_icon_image() -> Image.Image:
    """Load the project icon (largest .ico frame) for the system tray."""
    image = Image.open(resource_path(_ICON_NAME)).convert("RGBA")
    # LANCZOS (not Image.Resampling.LANCZOS) for Pillow 9.0 compat
    return image.resize((_ICON_SIZE, _ICON_SIZE), Image.LANCZOS)


def create_tray_icon(app: ColorPickerApp) -> pystray.Icon:
    """Create system tray icon with hide/show and exit menu."""
    def on_exit(icon: pystray.Icon, item: pystray.MenuItem) -> None:
        icon.stop()
        app.save_and_exit()

    def on_toggle(icon: pystray.Icon, item: pystray.MenuItem) -> None:
        app.toggle_visibility()

    menu = pystray.Menu(
        pystray.MenuItem("Hide/Show", on_toggle, default=True),
        pystray.MenuItem("Exit", on_exit),
    )

    icon = pystray.Icon(
        name="ColorPicker",
        icon=_load_icon_image(),
        title="Color Picker",
        menu=menu,
    )
    return icon


def run_tray(icon: pystray.Icon) -> None:
    """Run tray icon in a separate thread."""
    icon.run()
