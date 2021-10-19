import os


def test_push_commit_on_master(testcase):
    """Try pushing one single-file commit on master."""
    # Push master to the `origin' remote.  The delta should be one
    # commit with one file being modified.
    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: *** Invalid hooks.style-checker configuration ({cvs_check_script}):
remote: [Errno 2] No such file or directory: '{cvs_check_script}'
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
""".format(
        cvs_check_script=os.path.join(testcase.work_dir, "cvs_check.py")
    )

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
