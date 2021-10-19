def test_push_commit_on_master(testcase):
    """Try pushing one single-file commit on master."""
    p = testcase.run("git push origin master".split())

    expected_out = """\
remote: *** Error: hooks.mailinglist config option not set.
remote: *** Please contact your repository's administrator.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
