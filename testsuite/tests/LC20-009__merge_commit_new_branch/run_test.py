from support import *

class TestRun(TestCase):
    def test_push_branch_with_merge_commit(self):
        """Try pushing an update to master adding one merge commit.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master:topic/resync'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `README' `a' `c'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'topic/resync'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/topic/resync
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: ffb05b4a606fdb7b2919b209c725fe3b71880c00
remote:
remote: The branch 'topic/resync' was created pointing to:
remote:
remote:  ffb05b4... Merge topic branch fsf-head.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/topic/resync] New file README. Update a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/topic/resync
remote: X-Git-Oldrev: e02e15c547420b61fdc384c816e0e670ee8795b2
remote: X-Git-Newrev: 6d62250fdaed631cb170c0fc19c338accdba14ec
remote:
remote: commit 6d62250fdaed631cb170c0fc19c338accdba14ec
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu Dec 20 13:40:33 2012 +0400
remote:
remote:     New file README. Update a.
remote:
remote:     Some revision history info.
remote:
remote: Diff:
remote: ---
remote:  README | 3 +++
remote:  a      | 2 ++
remote:  2 files changed, 5 insertions(+)
remote:
remote: diff --git a/README b/README
remote: new file mode 100644
remote: index 0000000..13e6c1b
remote: --- /dev/null
remote: +++ b/README
remote: @@ -0,0 +1,3 @@
remote: +Some useful info.
remote: +
remote: +There.
remote: diff --git a/a b/a
remote: index e69de29..8dfae63 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -0,0 +1,2 @@
remote: +Some stuff about a.
remote: +Hello world.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/topic/resync] New file `c', update README accordingly.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/topic/resync
remote: X-Git-Oldrev: 6d62250fdaed631cb170c0fc19c338accdba14ec
remote: X-Git-Newrev: b4bfa84ef414162de60ff93005c5528f68b4c755
remote:
remote: commit b4bfa84ef414162de60ff93005c5528f68b4c755
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu Dec 20 13:41:24 2012 +0400
remote:
remote:     New file `c', update README accordingly.
remote:
remote:     README new refers to file `c'.
remote:     ChangeLog:
remote:
remote:             * c: New file.
remote:             * README: Add reference to new file `c'.
remote:
remote: Diff:
remote: ---
remote:  README | 1 +
remote:  c      | 1 +
remote:  2 files changed, 2 insertions(+)
remote:
remote: diff --git a/README b/README
remote: index 13e6c1b..32ed274 100644
remote: --- a/README
remote: +++ b/README
remote: @@ -1,3 +1,4 @@
remote:  Some useful info.
remote:
remote:  There.
remote: +Be sure to also read `c'.
remote: diff --git a/c b/c
remote: new file mode 100644
remote: index 0000000..e6a10da
remote: --- /dev/null
remote: +++ b/c
remote: @@ -0,0 +1 @@
remote: +Some other stuff about c.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/topic/resync] Merge topic branch fsf-head.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/topic/resync
remote: X-Git-Oldrev: 33e7556e39b638aa07f769bd894e75ed1af490dc
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
remote: ---
remote:  README | 4 ++++
remote:  a      | 2 ++
remote:  c      | 1 +
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
 * [new branch]      master -> topic/resync
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
