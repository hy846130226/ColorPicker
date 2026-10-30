import json
import os
import sys

DEFAULT_POSITION = (10, 10)


def _base_dir() -> str:
    # Frozen exe: config lives next to the exe; source run: next to this file.
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(name: str) -> str:
    # Frozen: bundled data extracted to sys._MEIPASS; source: script dir.
    base = sys._MEIPASS if getattr(sys, "frozen", False) else _base_dir()
    return os.path.join(base, name)


CONFIG_FILE = os.path.join(_base_dir(), "config.json")


def load_position() -> tuple[int, int]:
    """Load window position from config file. Returns default if file missing or corrupted."""
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_POSITION

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("window_x", DEFAULT_POSITION[0]), data.get("window_y", DEFAULT_POSITION[1])
    except (json.JSONDecodeError, KeyError):
        return DEFAULT_POSITION


def save_position(x: int, y: int) -> None:
    """Save window position to config file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump({"window_x": x, "window_y": y}, f)
