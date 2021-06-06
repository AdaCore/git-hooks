from support import *

class TestRun(TestCase):
    def test_push(self):
        """Try pushing branches with bad merges...
        """
        cd ('%s/repo' % TEST_DIR)

        # Try pushing "master".
        #
        # It contains a merge commit whose RH is the default RH
        # for merge commits.  The hooks should normally reject it,
        # except that the repository has been configured to disable
        # the associated check.  So the push should work.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Add new file b.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: a60540361d47901d3fe254271779f380d94645f7
remote: X-Git-Newrev: 80885319069c691f295150b51f478d99a36919c3
remote:
remote: commit 80885319069c691f295150b51f478d99a36919c3
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Dec 23 17:03:48 2012 +0400
remote:
remote:     Add new file b.
remote:
remote:     This is some other rh text.
remote:
remote: Diff:
remote: ---
remote:  b | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/b b/b
remote: new file mode 100644
remote: index 0000000..6ea0e45
remote: --- /dev/null
remote: +++ b/b
remote: @@ -0,0 +1 @@
remote: +A second file. No chance of conflict.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Merge branch 'topic'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: a89ee05260e5f0499f09dc36a9c3c1fd55fd4a79
remote: X-Git-Newrev: 3c799a3825af79b1a0f56b00ccc72a1e2837b4ed
remote:
remote: commit 3c799a3825af79b1a0f56b00ccc72a1e2837b4ed
remote: Merge: a89ee05 8088531
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Dec 23 17:09:24 2012 +0400
remote:
remote:     Merge branch 'topic'
remote:
remote: Diff:
remote: ---
remote:  b | 1 +
remote:  1 file changed, 1 insertion(+)
To ../bare/repo.git
   a89ee05..3c799a3  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Try pushing "master2".
        #
        # This time, it contains a merge commit whose revision
        # history was edited as expected, but the user forgot
        # to remove the "Conflicts:" section.  The push should
        # still be rejected despite the merge-commit-check config
        # option being set.
        p = Run('git push origin master2'.split())
        expected_out = """\
remote: *** Pattern "Conflicts:" has been detected.
remote: *** (in commit 2c7f984bac68db52f1f14cc312509c7242686390)
remote: ***
remote: *** This usually indicates a merge commit where some merge conflicts
remote: *** had to be resolved, but where the "Conflicts:" section has not
remote: *** been deleted from the revision history.
remote: ***
remote: *** Please edit the commit's revision history to either delete
remote: *** the section, or to avoid using the pattern above by itself.
remote: error: hook declined to update refs/heads/master2
To ../bare/repo.git
 ! [remote rejected] master2 -> master2 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
