from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing new branch on remote.

        In this testcase, the release-0.1-branch points to a commit
        that's one of the older commits in the "master" branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin release-0.1-branch'.split())
        expected_out = """\
remote: *** cvs_check: `trunk/repo/b'
remote: *** cvs_check: `trunk/repo/a'
remote: *** cvs_check: `trunk/repo/c'
remote: *** cvs_check: `trunk/repo/d'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Created branch release-0.1-branch
remote: X-ACT-checkin: repo
remote: X-Git-Refname: refs/heads/release-0.1-branch
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 4205e52273adad6b014e19fb1cf1fe1c9b8b4089
remote:
remote: The branch 'release-0.1-branch' was created pointing to:
remote:
remote:  4205e52... Generate update.
To ../bare/repo.git
 * [new branch]      release-0.1-branch -> release-0.1-branch
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

        # Verify that the branch has been created in the remote
        # repository and that it points to the expected commit.

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s release-0.1-branch'.split())
        expected_out = """\
4205e52273adad6b014e19fb1cf1fe1c9b8b4089
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
