import os


def test_no_sendmail_override_in_testsuite_mode(testcase):
    """Test behavior when sendmail not overridden in testsuite mode."""

    env = os.environ.copy()
    del env["GIT_HOOKS_SENDMAIL"]

    p = testcase.run("git push origin master".split(), env=env, ignore_environ=True)
    expected_out = """\
remote: *** The GIT_HOOKS_TESTSUITE_MODE environment variable is set,
remote: *** indicating that you are running the hooks in testsuite mode.
remote: *** In this mode, you must also define the GIT_HOOKS_SENDMAIL
remote: *** environment variable, pointing to a program to be called
remote: *** in place of the real sendmail.
remote: ***
remote: *** The goal is to catch situations where you forgot to
remote: *** prevent emails from being sent while using the hooks
remote: *** in a testing environment.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
