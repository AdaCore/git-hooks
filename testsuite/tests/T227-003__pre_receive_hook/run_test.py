import os


def test_push_commit_on_master(testcase):
    """Try pushing one single-file commit on master."""
    # First, adjust the project.config file to use a pre-receive-hook
    # script.  We can't do it any earlier, because we don't know
    # which temporary directory will be used when running this test.
    p = testcase.run(["git", "fetch", "origin", "refs/meta/config"])
    assert p.status == 0, p.image

    p = testcase.run(["git", "checkout", "FETCH_HEAD"])
    assert p.status == 0, p.image

    p = testcase.run(
        [
            "git",
            "config",
            "-f",
            "project.config",
            "--add",
            "hooks.pre-receive-hook",
            os.path.join(testcase.work_dir, "pre-receive-hook"),
        ]
    )
    assert p.status == 0, p.image

    p = testcase.run(
        [
            "git",
            "commit",
            "-m",
            "add hooks.pre-receive-hook config",
            "project.config",
        ]
    )
    assert p.status == 0, p.image

    p = testcase.run(["git", "push", "origin", "HEAD:refs/meta/config"])
    assert p.status == 0, p.image

    # Push master to the `origin' remote.  The pre-receive-hook
    # should be called (as evidenced by some debug output it prints),
    # and it should allow the update to get through.
    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: -----[ pre-receive-hook args ]-----
remote: -----[ pre-receive-hook stdin ]-----
remote: d065089ff184d97934c010ccd0e7e8ed94cb7165 a60540361d47901d3fe254271779f380d94645f7 refs/heads/master
remote: -----[ pre-recieve-hook end ]-----
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7
remote:
remote: commit a60540361d47901d3fe254271779f380d94645f7
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote:
remote: Diff:
remote: ---
remote:  a | 4 +++-
remote:  1 file changed, 3 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..a90d851 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,5 @@
remote:  Some file.
remote: -Second line.
remote: +Second line, in the middle.
remote: +In the middle too!
remote:  Third line.
remote: +
To ../bare/repo.git
   d065089..a605403  master -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
