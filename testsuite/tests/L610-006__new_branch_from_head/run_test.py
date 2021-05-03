from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing new branch on remote.

        In this situation, release-0.1-branch is a branch containing
        several commits attached to the HEAD of the master branch
        (master does not have any commit that release-0.1-branch does
        not have).
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin release-0.1-branch'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `a' `d'
remote: *** cvs_check: `repo' < `a' `b'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'release-0.1-branch'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/release-0.1-branch
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: dcc477c258baf8cf59db378fcc344dc962ad9a29
remote:
remote: The branch 'release-0.1-branch' was created pointing to:
remote:
remote:  dcc477c... New file b, add reference to it from file a.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/release-0.1-branch] A safe update.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/release-0.1-branch
remote: X-Git-Oldrev: dd6165c96db712d3e918fb5c61088b171b5e7cab
remote: X-Git-Newrev: d6b5dda3a77596bf77f84dfa20175b9c455a9853
remote:
remote: commit d6b5dda3a77596bf77f84dfa20175b9c455a9853
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun May 20 11:18:26 2012 +0200
remote:
remote:     A safe update.
remote:
remote:     Fixes a couple of critical issues.
remote:
remote: Diff:
remote: ---
remote:  a | 3 ++-
remote:  d | 1 +
remote:  2 files changed, 3 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 0a89c71..c4d61fe 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,2 +1,3 @@
remote:  This is a file
remote: -with a 2nd line.
remote: +with a 2nd line,
remote: +and a 3rd line.
remote: diff --git a/d b/d
remote: index 2def2d6..8985db4 100644
remote: --- a/d
remote: +++ b/d
remote: @@ -1,2 +1,3 @@
remote:  Title: D
remote:  This is a new file.
remote: +EOF
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/release-0.1-branch] New file b, add reference to it from file a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/release-0.1-branch
remote: X-Git-Oldrev: d6b5dda3a77596bf77f84dfa20175b9c455a9853
remote: X-Git-Newrev: dcc477c258baf8cf59db378fcc344dc962ad9a29
remote:
remote: commit dcc477c258baf8cf59db378fcc344dc962ad9a29
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun May 20 11:19:27 2012 +0200
remote:
remote:     New file b, add reference to it from file a.
remote:
remote:     Some additional information needed by this project.
remote:
remote: Diff:
remote: ---
remote:  a | 1 +
remote:  b | 1 +
remote:  2 files changed, 2 insertions(+)
remote:
remote: diff --git a/a b/a
remote: index c4d61fe..e58171a 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,4 @@
remote:  This is a file
remote:  with a 2nd line,
remote:  and a 3rd line.
remote: +See also: file `b'.
remote: diff --git a/b b/b
remote: new file mode 100644
remote: index 0000000..28fa4a8
remote: --- /dev/null
remote: +++ b/b
remote: @@ -0,0 +1 @@
remote: +Nearly empty file.
To ../bare/repo.git
 * [new branch]      release-0.1-branch -> release-0.1-branch
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Verify that the branch has been created in the remote
        # repository and that it points to the expected commit.

        cd('%s/bare/repo.git' % TEST_DIR)

        p = Run('git show-ref -s release-0.1-branch'.split())
        expected_out = """\
dcc477c258baf8cf59db378fcc344dc962ad9a29
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
