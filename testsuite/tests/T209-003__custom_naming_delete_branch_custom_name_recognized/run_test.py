from support import Run, TEST_DIR, TestCase, cd, runtests


class TestRun(TestCase):
    def test_delete_branch_custom_name_recognized(self):
        """Push a branch deletion using a custom reference name."""
        cd('%s/repo' % TEST_DIR)

        # Try to delete a branch with a custom name which does exist
        # in the remote repository, and is recognized by the naming
        # scheme as a branch. This should be accepted.
        p = Run('git push origin :refs/user/to-delete'
                .split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Deleted branch 'to-delete' in namespace 'refs/user'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/user/to-delete
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The branch 'to-delete' in namespace 'refs/user' was deleted.
remote: It previously pointed to:
remote:
remote:  d065089... New file: a.
To ../bare/repo.git
 - [deleted]         refs/user/to-delete
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Try to delete a branch with a reference name which is
        # recognized by the naming scheme as a branch, but does not
        # exist in the remote repository. This will obviously fail.
        p = Run('git push origin :refs/user/does-not-exist'
                .split())
        expected_out = """\
remote: *** unable to delete 'refs/user/does-not-exist': remote ref does not exist
remote: error: hook declined to update refs/user/does-not-exist
To ../bare/repo.git
 ! [remote rejected] refs/user/does-not-exist (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()

