def test_push_notes(testcase):
    """Try pushing our notes."""
    p = testcase.run("git push origin notes/commits".split())
    expected_out = """\
To ../bare/repo.git
 ! [rejected]        refs/notes/commits -> refs/notes/commits (fetch first)
error: failed to push some refs to '../bare/repo.git'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally. This is usually caused by another repository pushing
hint: to the same ref. You may want to first integrate the remote changes
hint: (e.g., 'git pull ...') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
"""
    if testcase.git_version() < "1.7.10":
        # Older versions of git generate the same error message
        # for current branches as they do for non-current branches,
        # whereas 1.7.10.4 generates two different outputs.
        # Fixup the expected output if testing with an older
        # version of git.
        expected_out = """\
To ../bare/repo.git
 ! [rejected]        refs/notes/commits -> refs/notes/commits (non-fast-forward)
error: failed to push some refs to '../bare/repo.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. Merge the remote changes (e.g. 'git pull')
hint: before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
"""
    elif testcase.git_version() < "1.8":
        # Slight differences in output...
        expected_out = """\
To ../bare/repo.git
 ! [rejected]        refs/notes/commits -> refs/notes/commits (non-fast-forward)
error: failed to push some refs to '../bare/repo.git'
hint: Updates were rejected because a pushed branch tip is behind its remote
hint: counterpart. Check out this branch and merge the remote changes
hint: (e.g. 'git pull') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
"""
    elif testcase.git_version() < "1.9":
        # Slight differences in output...
        expected_out = """\
To ../bare/repo.git
 ! [rejected]        refs/notes/commits -> refs/notes/commits (fetch first)
error: failed to push some refs to '../bare/repo.git'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally. This is usually caused by another repository pushing
hint: to the same ref. You may want to first merge the remote changes (e.g.,
hint: 'git pull') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Try again with -f, simulating a user trying to force
    # its way into getting this non-fast-forward update accepted.
    p = testcase.run("git push -f origin notes/commits".split())
    expected_out = """\
remote: *** Your Git Notes are not up to date.
remote: ***
remote: *** Please update your Git Notes and push again.
remote: error: hook declined to update refs/notes/commits
To ../bare/repo.git
 ! [remote rejected] refs/notes/commits -> refs/notes/commits (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
