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
        root.geometry("600x720")
        root.minsize(520, 600)
        latest = ttk.LabelFrame(root, text="Pick up where you left off", padding=10)
        latest.pack(fill="x", padx=10, pady=(10, 5))
        self.latest_label = ttk.Label(
            latest, text="", justify="left", font=("Menlo", 12), wraplength=560
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
        for entry in self.fields.values():
            entry.bind("<Return>", lambda event: self.save())
        self.fields["task"].focus_set()
        recent = ttk.LabelFrame(root, text="Recent snapshots", padding=10)
        recent.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        columns = ("id", "saved", "task", "tags")
        self.tree = ttk.Treeview(recent, columns=columns, show="headings", height=8)
        self.tree.heading("id", text="#")
        self.tree.heading("saved", text="Saved")
        self.tree.heading("task", text="Task")
        self.tree.heading("tags", text="Tags")
        self.tree.column("id", width=40, stretch=False, anchor="e")
        self.tree.column("saved", width=130, stretch=False)
        self.tree.column("task", width=240)
        self.tree.column("tags", width=120)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda event: self.show_selected())
        buttons = ttk.Frame(recent)
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(buttons, text="Delete", command=self.delete_selected).pack(side="right")
        ttk.Button(buttons, text="Show", command=self.show_selected).pack(side="right", padx=(0, 8))
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.refresh()

    def refresh(self) -> None:
        snap = storage.latest(self.conn)
        if snap is None:
            self.latest_label.config(text="No snapshots yet. Save one below.")
        else:
            self.latest_label.config(text=format_snapshot(snap))
        self.tree.delete(*self.tree.get_children())
        for s in storage.list_snapshots(self.conn, limit=50):
            self.tree.insert(
                "",
                "end",
                iid=str(s.id),
                values=(s.id, f"{s.created_at.astimezone():%Y-%m-%d %H:%M}", s.task, ", ".join(s.tags)),
            )
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
    def selected_id(self) -> int | None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("switchlog", "Select a snapshot in the list first.")
            return None
        return int(selection[0])
    def show_selected(self) -> None:
        snapshot_id = self.selected_id()
        if snapshot_id is None:
            return
        snap = storage.get(self.conn, snapshot_id)
        if snap is not None:
            self.latest_label.config(text=format_snapshot(snap))
    def delete_selected(self) -> None:
        snapshot_id = self.selected_id()
        if snapshot_id is None:
            return
        if not messagebox.askyesno("switchlog", f"Delete snapshot #{snapshot_id}? This cannot be undone."):
            return
        storage.delete(self.conn, snapshot_id)
        self.refresh()
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
