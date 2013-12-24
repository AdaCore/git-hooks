from support import *

class TestRun(TestCase):
    def test_push_branch_with_merge_commit(self):
        """Try pushing an update to master adding one merge commit.

        But the new master points to an already-existing commit
        (accessible from another branch, called topic/merge-stuff
        in this case).
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] (3 commits) Merge topic branch fsf-head.
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 33e7556e39b638aa07f769bd894e75ed1af490dc
remote: X-Git-Newrev: ffb05b4a606fdb7b2919b209c725fe3b71880c00
remote:
remote: The branch 'master' was updated to point to:
remote:
remote:  ffb05b4... Merge topic branch fsf-head.
remote:
remote: It previously pointed to:
remote:
remote:  33e7556... Add new file b.
remote:
remote: Diff:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   6d62250... New file README. Update a. (*)
remote:   b4bfa84... New file `c', update README accordingly. (*)
remote:   ffb05b4... Merge topic branch fsf-head. (*)
remote:
remote: (*) This commit already existed in another branch/reference.
remote:      No separate email sent.
To ../bare/repo.git
   33e7556..ffb05b4  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
