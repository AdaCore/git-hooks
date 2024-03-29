# coding=utf-8
import os


def test_push_commit_on_master(testcase):
    """Try pushing one commit on master."""
    # First, update the git-hooks configuration to install our
    # the script we want to use as our commit-email-formatter.

    testcase.update_git_hooks_config(
        [
            (
                "hooks.commit-email-formatter",
                os.path.join(testcase.work_dir, "commit-email-formatter.py"),
            )
        ]
    )

    # Push master to the `origin' remote.  The delta should be one
    # commit with one file being modified.
    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] foo.txt: Add title and a couple more examples of OK/not-OK.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 1a702b35451e923bf275c5e55c90de78e385e1ee
remote: X-Git-Newrev: f49c4cc90883d966a73b7c150c4cd6dd3ccb9827
remote:
remote: <<Email Body>>
remote:
remote: Diff:
remote: ---
remote:  foo.txt | 5 +++++
remote:  1 file changed, 5 insertions(+)
remote:
remote: diff --git a/foo.txt b/foo.txt
remote: index 3ff5971..d698ebb 100644
remote: --- a/foo.txt
remote: +++ b/foo.txt
remote: @@ -1,2 +1,7 @@
remote: +Title:
remote: +------
remote: +
remote:  “Alpha” <-- Two double-quote characters which are not ASCII.
remote:  shouldn’t <-- The quote character also isn't ASCII.
remote: +"ok" <-- This line is ASCII-compatible.
remote: +«double-brackets» <-- Also not ASCII.
To ../bare/repo.git
   1a702b3..f49c4cc  master -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
