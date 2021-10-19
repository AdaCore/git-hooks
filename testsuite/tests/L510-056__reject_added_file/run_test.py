def test_push_commit_on_master(testcase):
    """Try pushing multi-file commit on master."""
    # The push should fail, because the pre-commit checker will
    # refuse one of the updates.
    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: *** pre-commit check failed for commit: 16c509ed1a0f8b558f8ed9664a06b8cf905fc6b2
remote: *** cvs_check: `repo' < `b' `pck.adb' `pck.ads'
remote: *** ERROR: style-check error detected for file: `pck.ads'.
remote: *** ERROR: Copyright year in header is not up to date
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    assert p.status != 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
