def test_push_commit_on_master(testcase):
    """Push master as new ref with name outside standard namespace."""
    p = testcase.run("git push origin master:refs/for/master".split())
    expected_out = testcase.massage_git_output(
        """\
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'master' in namespace 'refs/for'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/for/master
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7
remote:
remote: The branch 'master' was created in namespace 'refs/for' pointing to:
remote:
remote:  a605403... Updated a.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo(refs/for/master)] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/for/master
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
 * [new reference]   master -> refs/for/master
"""
    )

    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)

    # Verify that the branch has been created in the remote
    # repository and that it points to the expected commit.

    p = testcase.run(
        "git show-ref -s refs/for/master".split(), cwd=testcase.bare_repo_dir
    )
    expected_out = """\
a60540361d47901d3fe254271779f380d94645f7
"""

    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
