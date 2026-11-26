import pytest


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("SWITCHLOG_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("SNAP_USER_DATA", raising=False)
    return tmp_path