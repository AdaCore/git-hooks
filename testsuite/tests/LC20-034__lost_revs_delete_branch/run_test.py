from support import *


class TestRun(TestCase):
    def test_delete_branch(testcase):
        """Test deleting topic branch causing commits to be lost."""
        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = testcase.run("git push origin :topic/experiment1".split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Deleted branch 'topic/experiment1'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
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

        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
