from support import Run, TEST_DIR, TestCase, cd, runtests


class TestRun(TestCase):
    def test_delete_branch_with_custom_name(self):
        """Delete a new branch with a custom reference name.
        """
        cd('%s/repo' % TEST_DIR)

        # First, try deleting with a branch name which exists and
        # is recognized by the repository's branch namespace.

        p = Run('git push origin :refs/user/to-delete'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
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

        # Next, try deleting a branch which does not exist.

        p = Run('git push origin :refs/user/does-not-exist'.split())
        expected_out = """\
remote: *** unable to delete 'refs/user/does-not-exist': remote ref does not exist
remote: error: hook declined to update refs/user/does-not-exist
To ../bare/repo.git
 ! [remote rejected] refs/user/does-not-exist (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Try deleting a branch which exists, but is not recognized
        # as a valid reference name for a branch.

        p = Run('git push origin :refs/others/exists-but-unrecognized'.split())
        expected_out = """\
remote: *** Unable to determine the type of reference for: refs/others/exists-but-unrecognized
remote: ***
remote: *** This repository currently recognizes the following types
remote: *** of references:
remote: ***
remote: ***  * Branches:
remote: ***       refs/heads/master
remote: ***       refs/heads/branches/.*
remote: ***       refs/vendor/.*
remote: ***       refs/user/.*
remote: ***
remote: ***  * Git Notes:
remote: ***       refs/notes/.*
remote: ***
remote: ***  * Tags:
remote: ***       refs/tags/.*
remote: error: hook declined to update refs/others/exists-but-unrecognized
To ../bare/repo.git
 ! [remote rejected] refs/others/exists-but-unrecognized (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Try deleting a reference which does not exist not is
        # recognized by the branch namespace.

        p = Run('git push origin :refs/does-not-exist/my-feature'.split())
        expected_out = """\
remote: *** unable to delete 'refs/does-not-exist/my-feature': remote ref does not exist
remote: error: hook declined to update refs/does-not-exist/my-feature
To ../bare/repo.git
 ! [remote rejected] refs/does-not-exist/my-feature (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)



if __name__ == '__main__':
    runtests()
