from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import Snapshot
from .paths import db_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    task TEXT NOT NULL,
    next_step TEXT,
    notes TEXT,
    links TEXT NOT NULL DEFAULT '[]',
    tags TEXT NOT NULL DEFAULT '[]',
    device TEXT NOT NULL
)
"""

def connect(path: Path | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(path or db_path())
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn
def save(conn: sqlite3.Connection, snap: Snapshot) -> Snapshot:
    cur = conn.execute(
        "INSERT INTO snapshots (uuid, created_at, task, next_step, notes, links, tags, device) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
            snap.uuid,
            snap.created_at.isoformat(),
            snap.task,
            snap.next_step,
            snap.notes,
            json.dumps(snap.links),
            json.dumps(snap.tags),
            snap.device,
        ),
    )
    conn.commit()
    snap.id = cur.lastrowid
    return snap
