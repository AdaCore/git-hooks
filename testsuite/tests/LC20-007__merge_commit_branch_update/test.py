from support import *

class TestRun(TestCase):
    def test_push_branch_with_merge_commit(self):
        """Try pushing an update to master adding one merge commit.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** cvs_check: `trunk/repo/a'
remote: *** cvs_check: `trunk/repo/b'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
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
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   6d62250... New file README. Update a. (*)
remote:   b4bfa84... New file `c', update README accordingly. (*)
remote:   ffb05b4... Merge topic branch fsf-head.
remote:
remote: (*) This commit already existed in another branch/reference.
remote:      No separate email sent.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Merge topic branch fsf-head.
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: b4bfa84ef414162de60ff93005c5528f68b4c755
remote: X-Git-Newrev: ffb05b4a606fdb7b2919b209c725fe3b71880c00
remote:
remote: commit ffb05b4a606fdb7b2919b209c725fe3b71880c00
remote: Merge: 33e7556 b4bfa84
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu Dec 20 13:50:25 2012 +0400
remote:
remote:     Merge topic branch fsf-head.
remote:
remote:     ChangeLog:
remote:
remote:             * a: Add stuff.
remote:             * c: New file.
remote:             * README: New file.
remote:
remote: Diff:
remote:
remote:  README |    4 ++++
remote:  a      |    2 ++
remote:  c      |    1 +
remote:  3 files changed, 7 insertions(+)
remote:
remote: diff --cc a
remote: index e0265ac,8dfae63..c5231c5
remote: --- a/a
remote: +++ b/a
remote: @@@ -1,2 -1,2 +1,4 @@@
remote:  +Some contents.
remote:  +Second line.
remote: + Some stuff about a.
remote: + Hello world.
To ../bare/repo.git
   33e7556..ffb05b4  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
