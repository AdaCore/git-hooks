def test_push_commit_on_master(testcase):
    """Try pushing one single-file commit on master.

    The commit contains one file rename, but we tell the hooks
    to treat renames as a new file, and thus expect to apply
    the pre-commit checks on the new file.
    """
    testcase.set_debug_level(2)

    # Push master to the `origin' remote.  The delta should be one
    # commit with one file being modified.
    p = testcase.run("git push origin master".split())
    expected_out = """\
remote:   DEBUG: check_update(ref_name=refs/heads/master, old_rev=a60540361d47901d3fe254271779f380d94645f7, new_rev=6a48cdab9b100506a387a8398af4751b33a4bfd0)
remote: DEBUG: validate_ref_update (refs/heads/master, a60540361d47901d3fe254271779f380d94645f7, 6a48cdab9b100506a387a8398af4751b33a4bfd0)
remote: DEBUG: update base: a60540361d47901d3fe254271779f380d94645f7
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: style_check_commit(old_rev=a60540361d47901d3fe254271779f380d94645f7, new_rev=6a48cdab9b100506a387a8398af4751b33a4bfd0)
remote:   DEBUG: deleted file ignored: a
remote: *** cvs_check: `repo' < `b'
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=a60540361d47901d3fe254271779f380d94645f7
remote:                         new_rev=6a48cdab9b100506a387a8398af4751b33a4bfd0)
remote: DEBUG: update base: a60540361d47901d3fe254271779f380d94645f7
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Rename A into B.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: a60540361d47901d3fe254271779f380d94645f7
remote: X-Git-Newrev: 6a48cdab9b100506a387a8398af4751b33a4bfd0
remote:
remote: commit 6a48cdab9b100506a387a8398af4751b33a4bfd0
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sun May 20 12:58:32 2012 +0200
remote:
remote:     Rename A into B.
remote:
remote: Diff:
remote: ---
remote:  a => b | 0
remote:  1 file changed, 0 insertions(+), 0 deletions(-)
remote:
remote: diff --git a/a b/b
remote: similarity index 100%
remote: rename from a
remote: rename to b
To ../bare/repo.git
   a605403..6a48cda  master -> master
"""

    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
