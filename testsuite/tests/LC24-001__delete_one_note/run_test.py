def test_push_notes(testcase):
    """Try pushing our notes."""
    p = testcase.run("git push origin notes/commits".split())
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [notes][repo] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/notes/commits
remote: X-Git-Oldrev: 58e8efaaf0dee13edea66b1abbd4b669132b3d77
remote: X-Git-Newrev: 5caa78def00f5293b84b13285d17f56844478d78
remote:
remote: Git notes annotating the following commit have been deleted.
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
remote:
remote: For the record, the references containing the annotated commit above are:
remote:
remote:     refs/heads/master
remote:
remote: diff --git a/a60540361d47901d3fe254271779f380d94645f7 b/a60540361d47901d3fe254271779f380d94645f7
remote: deleted file mode 100644
remote: index 8bd95e8..0000000
remote: --- a/a60540361d47901d3fe254271779f380d94645f7
remote: +++ /dev/null
remote: @@ -1 +0,0 @@
remote: -This is my first note.
To ../bare/repo.git
   58e8efa..5caa78d  refs/notes/commits -> refs/notes/commits
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
