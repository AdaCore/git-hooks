def test_delete_branch_with_std_name(testcase):
    """Push a branch deletion using a standard reference name."""
    p = testcase.run("git push origin :to-delete".split())
    expected_out = """\
remote: *** Deleting branches is not allowed for this repository.
remote: ***
remote: *** If you are trying to delete a branch which was created
remote: *** by mistake, contact an administrator, and ask him to
remote: *** temporarily change the repository's configuration
remote: *** so the branch can be deleted (he may elect to delete
remote: *** the branch himself to avoid the need to coordinate
remote: *** the operation).
remote: error: hook declined to update refs/heads/to-delete
To ../bare/repo.git
 ! [remote rejected] to-delete (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)


def test_delete_branch_with_custom_name(testcase):
    """Push a branch deletion using a custom reference name."""
    p = testcase.run("git push origin :refs/user/to-delete".split())
    expected_out = """\
remote: *** Deleting branches is not allowed for this repository.
remote: ***
remote: *** If you are trying to delete a branch which was created
remote: *** by mistake, contact an administrator, and ask him to
remote: *** temporarily change the repository's configuration
remote: *** so the branch can be deleted (he may elect to delete
remote: *** the branch himself to avoid the need to coordinate
remote: *** the operation).
remote: error: hook declined to update refs/user/to-delete
To ../bare/repo.git
 ! [remote rejected] refs/user/to-delete (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
