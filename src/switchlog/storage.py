from __future__ import annotations

import json
import sqlite3
from datetime import datetime
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
def _row_to_snapshot(row: sqlite3.Row) -> Snapshot:
    return Snapshot(
        id=row["id"],
        uuid=row["uuid"],
        created_at=datetime.fromisoformat(row["created_at"]),
        task=row["task"],
        next_step=row["next_step"],
        notes=row["notes"],
        links=json.loads(row["links"]),
        tags=json.loads(row["tags"]),
        device=row["device"],
    )
def list_snapshots(
    conn: sqlite3.Connection, limit: int | None = None, tag: str | None = None ) -> list[Snapshot]:
    rows = conn.execute(
        "SELECT * FROM snapshots ORDER BY created_at DESC, id DESC"
    ).fetchall()
    snaps = [_row_to_snapshot(r) for r in rows]
    if tag is not None:
        snaps = [s for s in snaps if tag in s.tags]
    if limit is not None:
        snaps = snaps[:limit]
    return snaps
def latest(conn: sqlite3.Connection) -> Snapshot | None:
    row = conn.execute(
        "SELECT * FROM snapshots ORDER BY created_at DESC, id DESC LIMIT 1"
    ).fetchone()
    return _row_to_snapshot(row) if row else None
def get(conn: sqlite3.Connection, snapshot_id: int) -> Snapshot | None:
    row = conn.execute(
        "SELECT * FROM snapshots WHERE id = ?", (snapshot_id,)
    ).fetchone()
    return _row_to_snapshot(row) if row else None
def delete(conn: sqlite3.Connection, snapshot_id: int) -> bool:
    cur = conn.execute("DELETE FROM snapshots WHERE id = ?", (snapshot_id,))
    conn.commit()
    return cur.rowcount > 0

