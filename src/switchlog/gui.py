from __future__ import annotations

import sys

from . import storage
from .cli import format_snapshot
from .models import Snapshot

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
def split_list(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


class SwitchlogApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.conn = storage.connect()
        root.title("switchlog")
        root.geometry("560x520")
        latest = ttk.LabelFrame(root, text="Pick up where you left off", padding=10)
        latest.pack(fill="x", padx=10, pady=(10, 5))
        self.latest_label = ttk.Label(
            latest, text="", justify="left", font=("Menlo", 12), wraplength=520
        )        
        self.latest_label.pack(anchor="w")
        form = ttk.LabelFrame(root, text="Save a snapshot", padding=10)
        form.pack(fill="x", padx=10, pady=5)
        form.columnconfigure(1, weight=1)
        self.fields: dict[str, ttk.Entry] = {}
        labels = [
            ("task", "Task *"),
            ("next_step", "Next step"),
            ("notes", "Notes"),
            ("links", "Links (comma-separated)"),
            ("tags", "Tags (comma-separated)"),
        ]
        for row, (key, label) in enumerate(labels):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=2)
            entry = ttk.Entry(form)
            entry.grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=2)
            self.fields[key] = entry
        ttk.Button(form, text="Save snapshot", command=self.save).grid(
            row=len(labels), column=1, sticky="e", pady=(8, 0)
        )
        root.bind("<Return>", lambda event: self.save())
        self.fields["task"].focus_set()
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.refresh()

    def refresh(self) -> None:
        snap = storage.latest(self.conn)
        if snap is None:
            self.latest_label.config(text="No snapshots yet. Save one below.")
        else:
            self.latest_label.config(text=format_snapshot(snap))
    def save(self) -> None:
        task = self.fields["task"].get().strip()
        if not task:
            messagebox.showwarning("switchlog", "Please describe what you are working on.")
            self.fields["task"].focus_set()
            return
        snap = Snapshot(
            task=task,
            next_step=self.fields["next_step"].get().strip() or None,
            notes=self.fields["notes"].get().strip() or None,
            links=split_list(self.fields["links"].get()),
            tags=split_list(self.fields["tags"].get()),
        )
        storage.save(self.conn, snap)
        for entry in self.fields.values():
            entry.delete(0, tk.END)
        self.refresh()
        self.fields["task"].focus_set()
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
