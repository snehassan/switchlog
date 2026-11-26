#where should the database files go

from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = "switchlog"

def data_dir() -> Path:
    override = os.environ.get("SWITCHLOG_DATA_DIR")
    if override:
        path = Path(override)
    elif "SNAP_USER_DATA" in os.environ:
        path = Path(os.environ["SNAP_USER_DATA"])
    else:
        path = Path(user_data_dir(APP_NAME))
    path.mkdir(parents=True, exist_ok=True)
    return path
def db_path() -> Path:
    return data_dir() / "switchlog.db"
