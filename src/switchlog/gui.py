from __future__ import annotations

import sys

from . import storage
from .cli import format_snapshot

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ModuleNotFoundError:
    tk = None
TK_HELP = (
    "switchlog-gui needs Tkinter, which this Python does not include.\n"
    "  macOS (Homebrew): brew install python-tk@<your Python version>\n"
    "  Ubuntu/Debian:    sudo apt install python3-tk\n"
    "The command-line tool, switchlog, works without it."
)


class SwitchlogApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.conn = storage.connect()
        root.title("switchlog")
        root.geometry("560x520")
        latest = ttk.LabelFrame(root, text="Pick up where you left off", padding=10)
        latest.pack(fill="x", padx=10, pady=(10, 5))
        self.latest_label = ttk.Label(latest, text="", justify="left", font=("Menlo", 12))
        self.latest_label.pack(anchor="w")
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.refresh()

    def refresh(self) -> None:
        snap = storage.latest(self.conn)
        if snap is None:
            self.latest_label.config(text="No snapshots yet. Save one below.")
        else:
            self.latest_label.config(text=format_snapshot(snap))

    def on_close(self) -> None:
        self.conn.close()
        self.root.destroy()


def main() -> int:
    if tk is None:
        print(TK_HELP, file=sys.stderr)
        return 1
    root = tk.Tk()
    SwitchlogApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
