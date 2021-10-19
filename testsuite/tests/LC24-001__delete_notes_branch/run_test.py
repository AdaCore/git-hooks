def test_delete_notes(testcase):
    """Try deleting the notes/commits branch."""
    p = testcase.run("git push origin :refs/notes/commits".split())
    expected_out = """\
remote: *** Deleting the Git Notes is not allowed.
remote: error: hook declined to update refs/notes/commits
To ../bare/repo.git
 ! [remote rejected] refs/notes/commits (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
