from support import *


class TestRun(TestCase):
    def test_pushes(testcase):
        """Push commits, and check effect (or not) of hooks.no-emails."""
        # First, try pushing branch "master". The hooks.no-emails config
        # contains "refs/heads/master", so this push should have no emails
        # being sent.

        p = testcase.run("git push origin master".split())
        expected_out = """\
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/heads/master',
remote: --  which matches the name of the reference being updated
remote: --  (refs/heads/master).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
   426fba3..4f0f08f  master -> master
"""

        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

        # Next, try pushing branch "master-with-emails". The no-emails
        # entry for "refs/heads/master" should be ignored in this case,
        # and thus emails are expected to be sent.

        p = testcase.run("git push origin master-with-emails".split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@example.com>
remote: To: commits@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/master-with-emails] Minor modifications.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master-with-emails
remote: X-Git-Oldrev: 426fba3571947f6de7f967e885a3168b9df7004a
remote: X-Git-Newrev: 8661ec1a498af1c06a49182edc7d106d46263481
remote:
remote: commit 8661ec1a498af1c06a49182edc7d106d46263481
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat May 5 15:23:36 2012 -0700
remote:
remote:     Minor modifications.
remote:
remote: Diff:
remote: ---
remote:  a | 2 +-
remote:  b | 2 +-
remote:  c | 1 -
remote:  3 files changed, 2 insertions(+), 3 deletions(-)
remote:
remote: diff --git a/a b/a
remote: index 78822b6..0a89c71 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,2 +1,2 @@
remote:  This is a file
remote: -with a second line.
remote: +with a 2nd line.
remote: diff --git a/b b/b
remote: index 373ad20..6ac1308 100644
remote: --- a/b
remote: +++ b/b
remote: @@ -1,3 +1,3 @@
remote:  some contents inside
remote:  that file
remote: -that isn't really all that interesting.
remote: +that is not really all that interesting.
remote: diff --git a/c b/c
remote: index 4bc3eed..e0f1ee1 100644
remote: --- a/c
remote: +++ b/c
remote: @@ -1,2 +1 @@
remote:  hello world.
remote: -ZZ
To ../bare/repo.git
   426fba3..8661ec1  master-with-emails -> master-with-emails
"""

        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
