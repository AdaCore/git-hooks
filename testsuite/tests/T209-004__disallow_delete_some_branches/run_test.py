from support import TEST_DIR, TestCase, cd, runtests


class TestRun(TestCase):
    def test_delete_branch_with_std_name(testcase):
        """Push a branch deletion using a standard reference name."""
        cd("%s/repo" % TEST_DIR)

        # First, try a branch which we are not allowed to delete.
        #
        # Note that the choice of branch to delete is not entirely innocent.
        # The repository's configuration has been set so that a branch
        # whose name is "to" can be deleted. This test _also_ makes sure
        # that this doesn't cause all branches whose name start with "to"
        # to be deletable.

        p = testcase.run("git push origin :to-delete".split())
        expected_out = """\
remote: *** Deleting branch 'to-delete' is not allowed.
remote: ***
remote: *** This repository currently only allow the deletion of references
remote: *** whose name matches the following:
remote: ***
remote: ***     refs/user/myself/.*
remote: ***     refs/heads/my-.*
remote: ***     refs/heads/to
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

        # Next, try with a branch which is allowed.
        #
        # Notice how we chose branch "to", here, to make sure that,
        # when we rejected the deletion of branch "to-delete" above,
        # it was because we missed the configuration allowing branch "to"
        # to be deleted, but rather because we decided that configuration
        # wasn't relevant for branch "to-delete".

        p = testcase.run("git push origin :to".split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Deleted branch 'to'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/to
remote: X-Git-Oldrev: 2a112bb1c30346f6287bb3d5c157a93235ea861f
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The branch 'to' was deleted.
remote: It previously pointed to:
remote:
remote:  2a112bb... update a to add terminator line
To ../bare/repo.git
 - [deleted]         to
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

    def test_delete_branch_with_custom_name(testcase):
        """Push a branch deletion using a custom reference name."""
        cd("%s/repo" % TEST_DIR)

        # First, try a branch which we are not allowed to delete.

        p = testcase.run("git push origin :refs/user/to-delete".split())
        expected_out = """\
remote: *** Deleting branch 'to-delete' in namespace 'refs/user' is not allowed.
remote: ***
remote: *** This repository currently only allow the deletion of references
remote: *** whose name matches the following:
remote: ***
remote: ***     refs/user/myself/.*
remote: ***     refs/heads/my-.*
remote: ***     refs/heads/to
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

        # Next, try with a branch which is allowed.

        p = testcase.run("git push origin :refs/user/myself/my-feature".split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Deleted branch 'myself/my-feature' in namespace 'refs/user'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/user/myself/my-feature
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The branch 'myself/my-feature' in namespace 'refs/user' was deleted.
remote: It previously pointed to:
remote:
remote:  d065089... New file: a.
To ../bare/repo.git
 - [deleted]         refs/user/myself/my-feature
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
