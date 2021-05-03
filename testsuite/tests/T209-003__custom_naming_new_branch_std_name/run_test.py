from support import Run, TEST_DIR, TestCase, cd, runtests


class TestRun(TestCase):
    def test_create_branch_with_standard_name(self):
        """Create a new branch with a standard reference name.
        """
        cd('%s/repo' % TEST_DIR)

        p = Run('git push origin master:new-master'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'new-master'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/new-master
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote:
remote: The branch 'new-master' was created pointing to:
remote:
remote:  d065089... New file: a.
To ../bare/repo.git
 * [new branch]      master -> new-master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
