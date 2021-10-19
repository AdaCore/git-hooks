def test_push_commit_on_master(testcase):
    """Try pushing one single-file commit on master."""
    # Push master to the `origin' remote.  The delta should be one
    # commit with one file being modified.
    p = testcase.run("git push origin master".split())
    expected_out = """\
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
remote: X-Git-Newrev: 1becc1a611a0059146a839001527229fa6f75569
remote:
remote: commit 1becc1a611a0059146a839001527229fa6f75569
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Added a lot of text to a, to triggger "diff truncated message".
remote:
remote: Diff:
remote: ---
remote:  a | 38 +++++++++++++++++++++++++++++++++++++-
remote:  1 file changed, 37 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..4f675c8 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,39 @@
remote:  Some file.
remote: -Seco[...]
remote:
remote: [diff truncated at 200 bytes]
remote:
To ../bare/repo.git
   d065089..1becc1a  master -> master
"""
    # There are some slight variations in the output of the stat
    # section of the diff, causing the truncation to occur at
    # a different location when using older versions of git
    # (1.7.8.2 in our case). Adjust the expected output accordingly.
    if testcase.git_version() < "1.7.10":
        expected_out = expected_out.replace("remote: -Se", "remote: -")

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
