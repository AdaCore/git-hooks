from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing new branch on remote.

        In this testcase, the release-0.1-branch points to a commit
        that's one of the older commits in the "master" branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin release-0.1-branch'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `b'
remote: *** cvs_check: `repo' < `a'
remote: *** cvs_check: `repo' < `c'
remote: *** cvs_check: `repo' < `d'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'release-0.1-branch'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/release-0.1-branch
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 4205e52273adad6b014e19fb1cf1fe1c9b8b4089
remote:
remote: The branch 'release-0.1-branch' was created pointing to:
remote:
remote:  4205e52... Generate update.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/release-0.1-branch] Update file b.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/release-0.1-branch
remote: X-Git-Oldrev: 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
remote: X-Git-Newrev: 2e5cfdf54f56b54de1d507e00b62ecc3de5addd3
remote:
remote: commit 2e5cfdf54f56b54de1d507e00b62ecc3de5addd3
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun May 20 11:27:32 2012 +0200
remote:
remote:     Update file b.
remote:
remote: Diff:
remote: ---
remote:  b | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/b b/b
remote: index 6ac1308..16dc8e4 100644
remote: --- a/b
remote: +++ b/b
remote: @@ -1,3 +1,4 @@
remote:  some contents inside
remote:  that file
remote:  that is not really all that interesting.
remote: +Add more text to make it interesting.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/release-0.1-branch] Generate update.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/release-0.1-branch
remote: X-Git-Oldrev: 2e5cfdf54f56b54de1d507e00b62ecc3de5addd3
remote: X-Git-Newrev: 4205e52273adad6b014e19fb1cf1fe1c9b8b4089
remote:
remote: commit 4205e52273adad6b014e19fb1cf1fe1c9b8b4089
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun May 20 11:28:28 2012 +0200
remote:
remote:     Generate update.
remote:
remote:     Should be safe enough for the release branch.
remote:
remote: Diff:
remote: ---
remote:  a | 3 ++-
remote:  c | 1 +
remote:  d | 1 +
remote:  3 files changed, 4 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 0a89c71..283b289 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,2 +1,3 @@
remote:  This is a file
remote: -with a 2nd line.
remote: +with a 2nd line,
remote: +and a third line.
remote: diff --git a/c b/c
remote: index 11ba4d0..9f8c405 100644
remote: --- a/c
remote: +++ b/c
remote: @@ -1,2 +1,3 @@
remote:  hello world.
remote:  This is file number C.
remote: +Have a look at D for a relatively empty file.
remote: diff --git a/d b/d
remote: index 6434b13..2954678 100644
remote: --- a/d
remote: +++ b/d
remote: @@ -1 +1,2 @@
remote:  This is a new file.
remote: +Some more text will be added later.
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
4205e52273adad6b014e19fb1cf1fe1c9b8b4089
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
