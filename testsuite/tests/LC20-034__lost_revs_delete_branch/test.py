from support import *

class TestRun(TestCase):
    def test_delete_branch(self):
        """Test deleting topic branch causing commits to be lost.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin :topic/experiment1'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Deleted branch topic/experiment1
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/heads/topic/experiment1
remote: X-Git-Oldrev: a60540361d47901d3fe254271779f380d94645f7
remote: X-Git-Newrev: 0000000000000000000000000000000000000000
remote:
remote: The branch 'topic/experiment1' was deleted.
remote: It previously pointed to:
remote:
remote:  a605403... Updated a.
remote:
remote: Diff:
remote:
remote: !!! WARNING: THE FOLLOWING COMMITS ARE NO LONGER ACCESSIBLE (LOST):
remote: -------------------------------------------------------------------
remote:
remote:   a605403... Updated a.
To ../bare/repo.git
 - [deleted]         topic/experiment1
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
