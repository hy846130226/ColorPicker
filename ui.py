import tkinter as tk

from color_picker import get_cursor_pos, get_pixel_color, rgb_to_hex
from config import load_position, resource_path, save_position

WINDOW_WIDTH = 280
WINDOW_HEIGHT = 190
PREVIEW_MIN_WIDTH = 90
REFRESH_MS = 50

ICON_NAME = "icons8-color-picker-48.ico"
BG = "#2b2b2b"
ENTRY_BG = "#3c3f41"
FG = "white"
BORDER = "#555555"
MAX_CHANNEL = 255
HEX_DIGITS = 6
ENTRY_STATE_READONLY = "readonly"


class ColorPickerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ColorPicker")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.configure(bg=BG)
        try:
            self.root.iconbitmap(resource_path(ICON_NAME))
        except tk.TclError:
            # 图标文件缺失不影响取色功能，忽略
            pass

        # Load saved position
        x, y = load_position()
        self.root.geometry(f"+{x}+{y}")
        self.root.protocol("WM_DELETE_WINDOW", self.save_and_exit)

        # Make window draggable (labels/preview/background only;
        # clicks on Entry/Radiobutton must not start a drag)
        self.root.bind("<Button-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._on_drag)
        self.root.bind("<ButtonRelease-1>", self._stop_drag)
        self._drag_data: dict[str, int] = {"x": 0, "y": 0}
        self._dragging: bool = False

        # Mode (Enable = live sampling, matching the old C# app default)
        self.mode_var = tk.StringVar(value="enable")
        enable_radio = tk.Radiobutton(
            self.root,
            text="Enable",
            variable=self.mode_var,
            value="enable",
            command=self._on_mode_change,
            bg=BG,
            fg=FG,
            selectcolor=ENTRY_BG,
            activebackground=BG,
            activeforeground=FG,
            highlightthickness=0,
            anchor="w",
        )
        enable_radio.grid(row=0, column=0, padx=12, pady=(10, 2), sticky="w")
        disable_radio = tk.Radiobutton(
            self.root,
            text="Disable",
            variable=self.mode_var,
            value="disable",
            command=self._on_mode_change,
            bg=BG,
            fg=FG,
            selectcolor=ENTRY_BG,
            activebackground=BG,
            activeforeground=FG,
            highlightthickness=0,
            anchor="w",
        )
        disable_radio.grid(row=0, column=1, padx=(0, 12), pady=(10, 2), sticky="w")
        self.root.grid_columnconfigure(2, weight=1)

        separator = tk.Frame(self.root, height=1, bg=BORDER)
        separator.grid(row=1, column=0, columnspan=3, padx=12, sticky="ew")

        # Body: R/G/B/HEX fields on the left, color preview on the right
        body = tk.Frame(self.root, bg=BG)
        body.grid(row=2, column=0, columnspan=3, padx=12, pady=(8, 12), sticky="nsew")
        self.root.grid_rowconfigure(2, weight=1)
        body.grid_columnconfigure(1, weight=1)
        for row in range(4):
            body.grid_rowconfigure(row, weight=1)

        self.r_var = tk.StringVar(value="0")
        self.g_var = tk.StringVar(value="0")
        self.b_var = tk.StringVar(value="0")
        self.hex_var = tk.StringVar(value="#000000")
        field_rows = (
            ("R:", self.r_var),
            ("G:", self.g_var),
            ("B:", self.b_var),
            ("HEX:", self.hex_var),
        )
        self._entries: list[tk.Entry] = []
        for row, (text, var) in enumerate(field_rows):
            label = tk.Label(
                body,
                text=text,
                width=5,
                anchor="w",
                bg=BG,
                fg=FG,
                font=("Consolas", 10),
            )
            label.grid(row=row, column=0, sticky="w", pady=2)
            entry = tk.Entry(
                body,
                textvariable=var,
                width=12,
                bg=ENTRY_BG,
                fg=FG,
                readonlybackground=ENTRY_BG,
                insertbackground=FG,
                relief="flat",
                font=("Consolas", 10),
                state=ENTRY_STATE_READONLY,
            )
            entry.grid(row=row, column=1, sticky="ew", pady=2, padx=(0, 8))
            entry.bind("<KeyRelease>", self._on_entry_changed)
            entry.bind("<Return>", self._on_entry_changed)
            entry.bind("<FocusOut>", self._on_focus_out)
            self._entries.append(entry)

        self.preview = tk.Frame(body, bg="#000000", width=PREVIEW_MIN_WIDTH, highlightthickness=1, highlightbackground=BORDER)
        self.preview.grid(row=0, column=2, rowspan=4, sticky="nsew", padx=(4, 0))
        body.grid_columnconfigure(2, minsize=PREVIEW_MIN_WIDTH)

        self._last_color: tuple[int, int, int] = (0, 0, 0)
        self._is_visible: bool = True
        self._timer_id: int | None = None

    def _start_drag(self, event) -> None:
        if isinstance(event.widget, (tk.Entry, tk.Radiobutton)):
            return
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._dragging = True

    def _on_drag(self, event) -> None:
        if not self._dragging:
            return
        x = self.root.winfo_x() + event.x - self._drag_data["x"]
        y = self.root.winfo_y() + event.y - self._drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    def _stop_drag(self, event) -> None:
        self._dragging = False
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def _dispatch(self, fn) -> None:
        # Tray/socket threads must not touch Tk directly; hop to the main loop.
        try:
            self.root.after(0, fn)
        except tk.TclError:
            # Window already destroyed during shutdown
            pass

    def _on_mode_change(self) -> None:
        if self.mode_var.get() == "disable":
            self._stop_sampling()
            self._set_entries_state(tk.NORMAL)
        else:
            self._set_entries_state(ENTRY_STATE_READONLY)
            self._start_sampling()

    def _set_entries_state(self, state: str) -> None:
        for entry in self._entries:
            entry.configure(state=state)

    def _start_sampling(self) -> None:
        if self._timer_id is None and self.mode_var.get() == "enable" and self._is_visible:
            self._timer_id = self.root.after(REFRESH_MS, self._update_color)

    def _stop_sampling(self) -> None:
        if self._timer_id is not None:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None

    def _update_color(self) -> None:
        try:
            x, y = get_cursor_pos()
            r, g, b = get_pixel_color(x, y)
            self._last_color = (r, g, b)
        except Exception:
            r, g, b = self._last_color

        self._set_fields(r, g, b)

        # Reschedule only while still sampling (Enable + visible);
        # a queued callback must not respawn the timer after hide/mode switch.
        self._timer_id = None
        self._start_sampling()

    def _set_fields(self, r: int, g: int, b: int) -> None:
        hex_color = rgb_to_hex(r, g, b)
        self.r_var.set(str(r))
        self.g_var.set(str(g))
        self.b_var.set(str(b))
        self.hex_var.set(hex_color)
        self.preview.configure(bg=hex_color)

    def _on_entry_changed(self, event=None) -> None:
        # Parse-or-skip: tolerate intermediate typing states.
        # Programmatic .set() never fires <KeyRelease>, so no re-entrancy guard is needed.
        if event is None or event.widget not in self._entries:
            return
        if event.keysym == "Return":
            self._normalize_all()
            return
        if event.widget in self._entries[:3]:
            color = self._parse_rgb()
            if color is not None:
                self._apply_rgb(color)
        else:
            color = self._parse_hex()
            if color is not None:
                self._apply_rgb(color)

    def _on_focus_out(self, event=None) -> None:
        if self.mode_var.get() == "enable":
            return
        self._normalize_all()

    def _parse_rgb(self) -> tuple[int, int, int] | None:
        try:
            r = int(self.r_var.get())
            g = int(self.g_var.get())
            b = int(self.b_var.get())
        except ValueError:
            return None
        if not all(0 <= v <= MAX_CHANNEL for v in (r, g, b)):
            return None
        return r, g, b

    def _parse_hex(self) -> tuple[int, int, int] | None:
        s = self.hex_var.get().strip()
        if s.startswith("#"):
            s = s[1:]
        if len(s) != HEX_DIGITS:
            return None
        try:
            value = int(s, 16)
        except ValueError:
            return None
        return (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF

    def _apply_rgb(self, color: tuple[int, int, int]) -> None:
        r, g, b = color
        self.r_var.set(str(r))
        self.g_var.set(str(g))
        self.b_var.set(str(b))
        hex_color = rgb_to_hex(r, g, b)
        self.hex_var.set(hex_color)
        self.preview.configure(bg=hex_color)

    def _normalize_all(self) -> None:
        # Clamp RGB channels into range; rewrite HEX as uppercase #RRGGBB
        # (self-healing from current RGB when unparseable), then re-sync.
        if self.mode_var.get() == "enable":
            return
        for var in (self.r_var, self.g_var, self.b_var):
            try:
                value = int(var.get())
            except ValueError:
                value = 0
            var.set(str(max(0, min(MAX_CHANNEL, value))))
        if self._parse_hex() is None:
            color = self._parse_rgb() or (0, 0, 0)
            self.hex_var.set(rgb_to_hex(*color))
        else:
            self.hex_var.set(rgb_to_hex(*self._parse_hex()))
        color = self._parse_rgb()
        if color is not None:
            self._apply_rgb(color)

    def run(self):
        """Start the color picker application."""
        self._start_sampling()
        self.root.mainloop()

    def hide(self) -> None:
        """Hide the window and stop the timer."""
        self._dispatch(self._hide_impl)

    def _hide_impl(self) -> None:
        if not self._is_visible:
            return
        self._is_visible = False
        self._stop_sampling()
        self.root.withdraw()

    def show(self) -> None:
        """Show the window and restart the timer."""
        self._dispatch(self._show_impl)

    def _show_impl(self) -> None:
        if self._is_visible:
            return
        self._is_visible = True
        self.root.deiconify()
        self._start_sampling()

    def toggle_visibility(self) -> None:
        """Toggle window visibility."""
        self._dispatch(self._toggle_visibility_impl)

    def _toggle_visibility_impl(self) -> None:
        if self._is_visible:
            self._hide_impl()
        else:
            self._show_impl()

    def save_and_exit(self) -> None:
        """Save window position and exit."""
        self._dispatch(self._save_and_exit_impl)

    def _save_and_exit_impl(self) -> None:
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        save_position(x, y)
        self.root.destroy()
