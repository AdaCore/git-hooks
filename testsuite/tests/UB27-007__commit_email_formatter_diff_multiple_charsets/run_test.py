# coding=utf-8
import os


def test_push_commit_on_master(testcase):
    """Try pushing one single-file commit on master.

    The purpose of this testcase is to verify that the git-hooks
    are able to pass the diff, which consists of 3 files all using
    a different charset (ASCII, ISO-8859-15, and UTF-8), down to
    the commit-email-formatter hook, without crashing.
    """
    # First, update the git-hooks configuration to install our
    # the script we want to use as our commit-email-formatter.

    p = testcase.run(["git", "fetch", "origin", "refs/meta/config"])
    testcase.assertEqual(p.status, 0, p.image)

    p = testcase.run(["git", "checkout", "FETCH_HEAD"])
    testcase.assertEqual(p.status, 0, p.image)

    p = testcase.run(
        [
            "git",
            "config",
            "--file",
            "project.config",
            "hooks.commit-email-formatter",
            os.path.join(testcase.work_dir, "commit-email-formatter.py"),
        ]
    )
    testcase.assertEqual(p.status, 0, p.image)

    p = testcase.run(
        [
            "git",
            "commit",
            "-m",
            "Add hooks.commit-email-formatter",
            "project.config",
        ]
    )
    testcase.assertEqual(p.status, 0, p.image)

    p = testcase.run(["git", "push", "origin", "HEAD:refs/meta/config"])
    testcase.assertEqual(p.status, 0, p.image)
    # Check the last line that git printed, and verify that we have
    # another piece of evidence that the change was succesfully pushed.
    assert "HEAD -> refs/meta/config" in p.out.splitlines()[-1], p.image

    # Return our current HEAD to branch "master". Not critical for
    # our testing, but it helps the testcase be closer to the more
    # typical scenarios.
    p = testcase.run(["git", "checkout", "master"])
    testcase.assertEqual(p.status, 0, p.image)

    # Push master to the `origin' remote.
    #
    # The "diff" covers 3 files which are using different file
    # encodings. The way we handle this in the commit email
    # where each diff is shown, is by guessing the original
    # encoding for each diff, decode that to unicode internally,
    # and then sending the email using a consistent encoding
    # across the entire email (utf-8).

    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Update all files
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d408c32bba64a79fc60dbda8fa047524f353e7cd
remote: X-Git-Newrev: 28fbd651f8161bcba746f5dbcecf5ec757241c1d
remote:
remote: commit 28fbd651f8161bcba746f5dbcecf5ec757241c1d
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun Nov 28 09:12:09 2021 +0400
remote:
remote:     Update all files
remote:
remote: Diff:
remote: ---
remote:  ascii.txt       | 1 +
remote:  iso-8859-15.txt | 1 +
remote:  utf-8.txt       | 1 +
remote:  3 files changed, 3 insertions(+)
remote:
remote: diff --git a/ascii.txt b/ascii.txt
remote: index d94f50b..19fe92b 100644
remote: --- a/ascii.txt
remote: +++ b/ascii.txt
remote: @@ -1 +1,2 @@
remote:  This is a file with ASCII text only.
remote: +Pretty restricted charset.
remote: diff --git a/iso-8859-15.txt b/iso-8859-15.txt
remote: index c629aad..555625f 100644
remote: --- a/iso-8859-15.txt
remote: +++ b/iso-8859-15.txt
remote: @@ -1 +1,2 @@
remote:  Español: ¿ Cómo te llamas, niño?
remote: +Français: Un œuf corse (ou devrions nous dire «corsé»?)
remote: diff --git a/utf-8.txt b/utf-8.txt
remote: index ea83122..e29a0f4 100644
remote: --- a/utf-8.txt
remote: +++ b/utf-8.txt
remote: @@ -1 +1,2 @@
remote:  日本: 次のファイルから読み込み
remote: +ประเทศไทย: ขอขอบคุณ
To ../bare/repo.git
   d408c32..28fbd65  master -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
