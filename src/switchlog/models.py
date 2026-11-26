from __future__ import annotations
import socket
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class Snapshot:
    task: str
    next_step: str | None = None
    notes: str | None = None
    links: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    device: str = field(default_factory=socket.gethostname)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: int | None = None