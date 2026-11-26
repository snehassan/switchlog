from switchlog import storage
from switchlog.models import Snapshot


def test_save_assigns_id_and_round_trips():
    conn = storage.connect()
    saved = storage.save(conn, Snapshot(task="t", links=["https://a"], tags=["work"]))
    loaded = storage.get(conn, saved.id)
    assert loaded == saved
def test_list_is_newest_first_and_filters_by_tag():
    conn = storage.connect()
    storage.save(conn, Snapshot(task="old", tags=["work"]))
    storage.save(conn, Snapshot(task="new", tags=["home"]))
    assert [s.task for s in storage.list_snapshots(conn)] == ["new", "old"]
    assert [s.task for s in storage.list_snapshots(conn, tag="work")] == ["old"]
def test_latest_is_none_when_empty():
    assert storage.latest(storage.connect()) is None


def test_delete_reports_whether_anything_was_removed():
    conn = storage.connect()
    s = storage.save(conn, Snapshot(task="t"))
    assert storage.delete(conn, s.id) is True
    assert storage.delete(conn, s.id) is False