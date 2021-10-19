import os


def test_push_commit_on_master(testcase):
    """Try pushing multiple commits on master."""
    # First, adjust the project.config file to use an update-hook
    # script.  We have to do it manually here, because we need to
    # provide the full path to that script.
    with open("%s/hooks_config" % testcase.work_dir) as f:
        project_config = f.read() % {"TEST_DIR": testcase.work_dir}
    with open(os.path.join(testcase.repo_dir, "project.config"), "w") as f:
        f.write(project_config)
    p = testcase.run(
        ["git", "commit", "-m", "Add hooks.update-hook config", "project.config"]
    )
    assert p.status == 0, p.image

    p = testcase.run(
        ["git", "push", "origin", "refs/heads/meta/config:refs/meta/config"]
    )
    assert p.status == 0, p.image

    p = testcase.run("git checkout master".split())
    assert p.status == 0, p.image

    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: *** Update rejected by this repository's hooks.update-hook script
remote: *** ({testcase.work_dir}/update-hook):
remote: *** -----[ update-hook args ]-----
remote: *** 'refs/heads/master'
remote: *** '426fba3571947f6de7f967e885a3168b9df7004a'
remote: *** 'dd6165c96db712d3e918fb5c61088b171b5e7cab'
remote: *** -----[ update-hook stdin ]-----
remote: *** -----[ update-hook end ]-----
remote: *** Error: Updates of this branch (refs/heads/master) are not allowed.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
""".format(
        testcase=testcase
    )

    assert p.status != 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
