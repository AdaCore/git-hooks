import os


def test_no_sendmail(testcase):
    """Test behavior when sendmail program cannot be found."""

    # Point the git-hooks to use a sendmail program that does not
    # exist...
    bad_sendmail_path = os.path.join(testcase.work_dir, "bad-sendmail")
    env = {"GIT_HOOKS_SENDMAIL": bad_sendmail_path}

    p = testcase.run("git push origin master".split(), env=env)
    expected_out = """\
remote: *** Cannot find sendmail at either of the following locations:
remote: ***  - {bad_sendmail_path}
remote: ***
remote: *** Please contact your system administrator.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
""".format(
        bad_sendmail_path=bad_sendmail_path
    )

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
