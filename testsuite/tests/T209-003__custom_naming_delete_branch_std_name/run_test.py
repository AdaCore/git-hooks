from support import Run, TEST_DIR, TestCase, cd, runtests


class TestRun(TestCase):
    def test_delete_branch_with_std_name(self):
        """Push a branch deletion using a standard reference name."""
        cd('%s/repo' % TEST_DIR)

        p = Run('git push origin :to-delete'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Deleted branch 'to-delete'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/to-delete
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The branch 'to-delete' was deleted.
remote: It previously pointed to:
remote:
remote:  d065089... New file: a.
To ../bare/repo.git
 - [deleted]         to-delete
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
