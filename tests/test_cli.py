from switchlog.cli import main


def test_save_then_resume(capsys):
    assert main(["save", "fixing auth bug", "--next", "write test", "--tag", "work"]) == 0
    assert main(["resume"]) == 0
    out = capsys.readouterr().out
    assert "fixing auth bug" in out
    assert "next:   write test" in out
def test_resume_with_no_snapshots_fails_helpfully(capsys):
    assert main(["resume"]) == 1
    assert "switchlog save" in capsys.readouterr().err


def test_show_unknown_id(capsys):
    assert main(["show", "99"]) == 1
    assert "No snapshot with ID 99" in capsys.readouterr().err