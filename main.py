import threading

from single_instance import try_activate_existing, start_server
from tray import create_tray_icon, run_tray
from ui import ColorPickerApp


def main() -> None:
    if try_activate_existing():
        return

    app = ColorPickerApp()
    start_server(app.show)

    icon = create_tray_icon(app)

    # Run tray icon in a separate daemon thread so it exits when the main loop ends
    tray_thread = threading.Thread(target=run_tray, args=(icon,), daemon=True)
    tray_thread.start()

    # Run main UI loop (blocks until window is closed)
    app.run()


if __name__ == "__main__":
    main()
