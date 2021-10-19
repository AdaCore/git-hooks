def test_push_commit_on_master(testcase):
    """Try pushing master..."""
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
remote: X-Git-Newrev: 599087bd0d73bb71d0858c4db01a11aebadc31cd
remote:
remote: commit 599087bd0d73bb71d0858c4db01a11aebadc31cd
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote:
remote:     no-tn-check
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
   d065089..599087b  master -> master
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)


def test_push_commit_on_badleft(testcase):
    """Try pushing badleft..."""
    p = testcase.run("git push origin badleft".split())
    expected_out = """\
remote: *** The following commit is missing a ticket number inside
remote: *** its revision history.  If the change is sufficiently
remote: *** minor that a ticket number is not meaningful, please use
remote: *** the word "no-tn-check" in place of a ticket number.
remote: ***
remote: *** commit 4745a4f1ab22602a78540b16d45e37f0f5c95574
remote: *** Subject: Updated a.
remote: error: hook declined to update refs/heads/badleft
To ../bare/repo.git
 ! [remote rejected] badleft -> badleft (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)


def test_push_commit_on_badright(testcase):
    """Try pushing badright..."""
    p = testcase.run("git push origin badright".split())
    expected_out = """\
remote: *** The following commit is missing a ticket number inside
remote: *** its revision history.  If the change is sufficiently
remote: *** minor that a ticket number is not meaningful, please use
remote: *** the word "no-tn-check" in place of a ticket number.
remote: ***
remote: *** commit fd9612bc6e944313396198fe9a7361bdae032e52
remote: *** Subject: Updated a.
remote: error: hook declined to update refs/heads/badright
To ../bare/repo.git
 ! [remote rejected] badright -> badright (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
