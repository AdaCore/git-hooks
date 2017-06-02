from support import *

class TestRun(TestCase):
    def test_push_branch_with_merge_commit(self):
        """Try pushing an update to master adding one merge commit.
        """
        cd ('%s/repo' % TEST_DIR)

        # First, adjust the project.config file to use a commit-filer
        # script.  We have to do it manually here, because we need to
        # provide the full path to that script.
        with open('%s/hooks_config' % TEST_DIR) as f:
            project_config = f.read() % {'TEST_DIR': TEST_DIR}
        with open('project.config', 'w') as f:
            f.write(project_config)
        p = Run(['git', 'commit', '-m', 'fix hooks.mailinglist',
                 'project.config'])
        self.assertTrue(p.status == 0, p.image)

        p = Run(['git', 'push', 'origin',
                 'refs/heads/meta/config:refs/meta/config'])
        self.assertTrue(p.status == 0, p.image)

        p = Run('git checkout master'.split())
        self.assertTrue(p.status == 0, p.image)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `README'
remote: *** cvs_check: `repo' < `a'
remote: *** cvs_check: `repo' < `c'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] (3 commits) Merge topic branch fsf-head.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
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
remote:   ffb05b4... Merge topic branch fsf-head.
remote:   b4bfa84... New file `c', update README accordingly. (*)
remote:   6d62250... New file README. Update a. (*)
remote:
remote: (*) This commit exists in a branch whose name matches
remote:     the hooks.noemail config option. No separate email
remote:     sent.
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
remote: commit 6d62250fdaed631cb170c0fc19c338accdba14ec
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu Dec 20 13:40:33 2012 +0400
remote:
remote:     New file README. Update a.
remote:
remote:     Some revision history info.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Merge topic branch fsf-head.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
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
remote:
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
remote: -----[ commit-filer start ]-----
remote: '-G'
remote: 'gdb binutils'
remote: -----[ commit-filer body ]-----
remote: The master branch has been updated by Test Suite <testsuite@adacore.com>:
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
remote: -----[ commit-filer end ]-----
remote:
To ../bare/repo.git
   33e7556..ffb05b4  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
