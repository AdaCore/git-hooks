from support import *


class TestRun(TestCase):
    def test_submitter_email(testcase):
        """Call post-receive hook with --submitter-email."""
        cd("%s/bare/repo.git" % TEST_DIR)

        p = testcase.run(
            ["./hooks/post-receive", "--submitter-email=Dave Smith <ds@example.com>"],
            input=(
                "|d065089ff184d97934c010ccd0e7e8ed94cb7165"
                " a60540361d47901d3fe254271779f380d94645f7"
                " refs/heads/master"
            ),
        )

        expected_out = """\
DEBUG: MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Type: text/plain; charset="utf-8"
From: Dave Smith <ds@example.com>
To: git-hooks-ci@example.com
Bcc: filer@example.com
Subject: [repo] Updated a.
X-Act-Checkin: repo
X-Git-Author: Joel Brobecker <brobecker@adacore.com>
X-Git-Refname: refs/heads/master
X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7

commit a60540361d47901d3fe254271779f380d94645f7
Author: Joel Brobecker <brobecker@adacore.com>
Date:   Fri Apr 27 13:08:29 2012 -0700

    Updated a.

    Just added a little bit of text inside file a.
    Thought about doing something else, but not really necessary.

Diff:
---
 a | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)

diff --git a/a b/a
index 01d0f12..a90d851 100644
--- a/a
+++ b/a
@@ -1,3 +1,5 @@
 Some file.
-Second line.
+Second line, in the middle.
+In the middle too!
 Third line.
+
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
