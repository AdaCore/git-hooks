def test_push_gdb_head(testcase):
    """Try pushing gdb-head.

    The push introduces a merge commit whose revision log contains
    a special keyword telling the hooks to skip the pre-commit-checks
    phase entirely.
    """
    # Set the debug level to 1, in order to see the debug trace
    # confirming that the no-precommit-check keyword was picked up
    # by the hooks.
    testcase.set_debug_level(1)

    # Push gdb-head to the `origin' remote.  The delta should be one
    # commit with one file being modified.
    p = testcase.run("git push origin gdb-head".split())
    expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/gdb-head, 2c2cd0d654cc6cf460024feb845ee7ea760290c4, 8da5e84724007accbaf409022c3c9f07776a8c8b)
remote: DEBUG: update base: 2c2cd0d654cc6cf460024feb845ee7ea760290c4
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: style_check_commit(old_rev=2c2cd0d654cc6cf460024feb845ee7ea760290c4, new_rev=8da5e84724007accbaf409022c3c9f07776a8c8b)
remote: DEBUG: pre-commit checks explicity disabled for commit 8da5e84724007accbaf409022c3c9f07776a8c8b
remote: DEBUG: post_receive_one(ref_name=refs/heads/gdb-head
remote:                         old_rev=2c2cd0d654cc6cf460024feb845ee7ea760290c4
remote:                         new_rev=8da5e84724007accbaf409022c3c9f07776a8c8b)
remote: DEBUG: update base: 2c2cd0d654cc6cf460024feb845ee7ea760290c4
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: nowhere@example.com
remote: Subject: [repo/gdb-head] (2 commits) Resync from fsf-master as of today -- no-precommit-check
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/gdb-head
remote: X-Git-Oldrev: 2c2cd0d654cc6cf460024feb845ee7ea760290c4
remote: X-Git-Newrev: 8da5e84724007accbaf409022c3c9f07776a8c8b
remote:
remote: The branch 'gdb-head' was updated to point to:
remote:
remote:  8da5e84... Resync from fsf-master as of today -- no-precommit-check
remote:
remote: It previously pointed to:
remote:
remote:  2c2cd0d... AdaCore-specific change of bcd.
remote:
remote: Diff:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   8da5e84... Resync from fsf-master as of today -- no-precommit-check
remote:   6a9155b... 2016 copyright header yearly update. (*)
remote:
remote: (*) This commit exists in a branch whose name matches
remote:     the hooks.noemail config option. No separate email
remote:     sent.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: nowhere@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/gdb-head] Resync from fsf-master as of today -- no-precommit-check
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/gdb-head
remote: X-Git-Oldrev: 2c2cd0d654cc6cf460024feb845ee7ea760290c4
remote: X-Git-Newrev: 8da5e84724007accbaf409022c3c9f07776a8c8b
remote:
remote: commit 8da5e84724007accbaf409022c3c9f07776a8c8b
remote: Merge: 2c2cd0d 6a9155b
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Apr 23 19:17:33 2016 -0400
remote:
remote:     Resync from fsf-master as of today -- no-precommit-check
remote:
remote: Diff:
remote: ---
remote:  a.txt      | 2 +-
remote:  bcd        | 2 +-
remote:  sub/ab.txt | 2 +-
remote:  3 files changed, 3 insertions(+), 3 deletions(-)
remote:
remote: diff --cc bcd
remote: index fd49d8d,0823230..3383953
remote: --- a/bcd
remote: +++ b/bcd
remote: @@@ -1,4 -1,3 +1,4 @@@
remote: - Copyright (C) 2015 AdaCore
remote: + Copyright (C) 2015-2016 AdaCore
remote:
remote:   This is bcd, with lots of interesting stuff it in.
remote:  +And then this is an AdaCore-specific change.
To ../bare/repo.git
   2c2cd0d..8da5e84  gdb-head -> gdb-head
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
