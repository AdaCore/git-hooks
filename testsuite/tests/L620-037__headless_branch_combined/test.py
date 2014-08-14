from support import *
import os

class TestRun(TestCase):
    def test_push(self):
        """Try pushing head-less branch (called "headless") on master.
        Same with head-less branch (called "one-commit") on master.
        The test with the "one-commit" branch is just to test the
        situation where the new head-less branch only has one commit.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debugs to verify that the hooks pick the correct
        # commit as the first commit.
        self.set_debug_level(1)

        # First, push the headless branch.

        p = Run('git push origin headless'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/headless, 0000000000000000000000000000000000000000, 902092ffe1cf61b28e28c86949a447b9fc2591a4)
remote: DEBUG: update base: None
remote: DEBUG: (combined style checking)
remote: DEBUG: check_commit(old_rev=None, new_rev=902092ffe1cf61b28e28c86949a447b9fc2591a4)
remote: DEBUG: check_commit: old_rev -> 4b825dc642cb6eb9a060e54bf8d69288fbee4904 (empty tree SHA1)
remote: *** cvs_check: `trunk/repo/that.txt'
remote: *** cvs_check: `trunk/repo/there'
remote: *** cvs_check: `trunk/repo/this.txt'
remote: DEBUG: post_receive_one(ref_name=refs/heads/headless
remote:                         old_rev=0000000000000000000000000000000000000000
remote:                         new_rev=902092ffe1cf61b28e28c86949a447b9fc2591a4)
remote: DEBUG: update base: None
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'headless'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/headless
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 902092ffe1cf61b28e28c86949a447b9fc2591a4
remote:
remote: The branch 'headless' was created pointing to:
remote:
remote:  902092f... Forgot to update this.txt in the previous commit.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/headless] Initial commit.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/headless
remote: X-Git-Oldrev:
remote: X-Git-Newrev: 27ebebdd36a485235982f54e8ae68dfea6432c87
remote:
remote: commit 27ebebdd36a485235982f54e8ae68dfea6432c87
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Jun 15 12:35:26 2012 -0700
remote:
remote:     Initial commit.
remote:
remote: Diff:
remote: ---
remote:  that.txt | 1 +
remote:  this.txt | 1 +
remote:  2 files changed, 2 insertions(+)
remote:
remote: diff --git a/that.txt b/that.txt
remote: new file mode 100644
remote: index 0000000..9e0a19c
remote: --- /dev/null
remote: +++ b/that.txt
remote: @@ -0,0 +1 @@
remote: +some more stuff.
remote: diff --git a/this.txt b/this.txt
remote: new file mode 100644
remote: index 0000000..6caa1ff
remote: --- /dev/null
remote: +++ b/this.txt
remote: @@ -0,0 +1 @@
remote: +some stuff.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/headless] Small update. Add file "there" as well.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/headless
remote: X-Git-Oldrev: 27ebebdd36a485235982f54e8ae68dfea6432c87
remote: X-Git-Newrev: 6586d1c0db5147a521975c15cc6bfd92d2f66de6
remote:
remote: commit 6586d1c0db5147a521975c15cc6bfd92d2f66de6
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Jun 15 12:36:37 2012 -0700
remote:
remote:     Small update. Add file "there" as well.
remote:
remote: Diff:
remote: ---
remote:  that.txt | 2 +-
remote:  there    | 1 +
remote:  2 files changed, 2 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/that.txt b/that.txt
remote: index 9e0a19c..b2bb76b 100644
remote: --- a/that.txt
remote: +++ b/that.txt
remote: @@ -1 +1 @@
remote: -some more stuff.
remote: +some more cool stuff.
remote: diff --git a/there b/there
remote: new file mode 100644
remote: index 0000000..4879b9f
remote: --- /dev/null
remote: +++ b/there
remote: @@ -0,0 +1 @@
remote: +That's where you can find it.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/headless] Forgot to update this.txt in the previous commit.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/headless
remote: X-Git-Oldrev: 6586d1c0db5147a521975c15cc6bfd92d2f66de6
remote: X-Git-Newrev: 902092ffe1cf61b28e28c86949a447b9fc2591a4
remote:
remote: commit 902092ffe1cf61b28e28c86949a447b9fc2591a4
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Jun 15 12:36:59 2012 -0700
remote:
remote:     Forgot to update this.txt in the previous commit.
remote:
remote: Diff:
remote: ---
remote:  this.txt | 2 +-
remote:  1 file changed, 1 insertion(+), 1 deletion(-)
remote:
remote: diff --git a/this.txt b/this.txt
remote: index 6caa1ff..514129d 100644
remote: --- a/this.txt
remote: +++ b/this.txt
remote: @@ -1 +1 @@
remote: -some stuff.
remote: +some cool stuff.
To ../bare/repo.git
 * [new branch]      headless -> headless
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Next, push the one-commit branch.

        p = Run('git push origin one-commit'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/one-commit, 0000000000000000000000000000000000000000, ef3ab848df2bef804d5bd0880475d40cb6aab0bf)
remote: DEBUG: update base: None
remote: DEBUG: (combined style checking)
remote: DEBUG: check_commit(old_rev=None, new_rev=ef3ab848df2bef804d5bd0880475d40cb6aab0bf)
remote: DEBUG: check_commit: old_rev -> 4b825dc642cb6eb9a060e54bf8d69288fbee4904 (empty tree SHA1)
remote: *** cvs_check: `trunk/repo/contents.txt'
remote: *** cvs_check: `trunk/repo/stuff'
remote: DEBUG: post_receive_one(ref_name=refs/heads/one-commit
remote:                         old_rev=0000000000000000000000000000000000000000
remote:                         new_rev=ef3ab848df2bef804d5bd0880475d40cb6aab0bf)
remote: DEBUG: update base: None
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'one-commit'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/one-commit
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: ef3ab848df2bef804d5bd0880475d40cb6aab0bf
remote:
remote: The branch 'one-commit' was created pointing to:
remote:
remote:  ef3ab84... Initial commit.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/one-commit] Initial commit.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/one-commit
remote: X-Git-Oldrev:
remote: X-Git-Newrev: ef3ab848df2bef804d5bd0880475d40cb6aab0bf
remote:
remote: commit ef3ab848df2bef804d5bd0880475d40cb6aab0bf
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Jun 20 08:33:18 2012 -0700
remote:
remote:     Initial commit.
remote:
remote: Diff:
remote: ---
remote:  contents.txt | 1 +
remote:  stuff        | 1 +
remote:  2 files changed, 2 insertions(+)
remote:
remote: diff --git a/contents.txt b/contents.txt
remote: new file mode 100644
remote: index 0000000..531af94
remote: --- /dev/null
remote: +++ b/contents.txt
remote: @@ -0,0 +1 @@
remote: +This repository will contain some stuff.
remote: diff --git a/stuff b/stuff
remote: new file mode 100644
remote: index 0000000..60ddd81
remote: --- /dev/null
remote: +++ b/stuff
remote: @@ -0,0 +1 @@
remote: +bits and bytes.
To ../bare/repo.git
 * [new branch]      one-commit -> one-commit
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
