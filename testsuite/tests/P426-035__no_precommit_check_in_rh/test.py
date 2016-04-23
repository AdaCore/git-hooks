from support import *

class TestRun(TestCase):
    def test_push_gdb_head(self):
        """Try pushing gdb-head.

        The push introduces a merge commit whose revision log contains
        a special keyword telling the hooks to skip the pre-commit-checks
        phase entirely.
        """
        cd ('%s/repo' % TEST_DIR)

        # Set the debug level to 1, in order to see the debug trace
        # confirming that the no-precommit-check keyword was picked up
        # by the hooks.
        self.set_debug_level(1)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin gdb-head'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/gdb-head, 2c2cd0d654cc6cf460024feb845ee7ea760290c4, 82f09a220fc59bcdb40896e910bce208c3810b60)
remote: DEBUG: update base: 2c2cd0d654cc6cf460024feb845ee7ea760290c4
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=2c2cd0d654cc6cf460024feb845ee7ea760290c4, new_rev=82f09a220fc59bcdb40896e910bce208c3810b60)
remote: DEBUG: pre-commit checks explicity disabled for commit 82f09a220fc59bcdb40896e910bce208c3810b60
remote: DEBUG: post_receive_one(ref_name=refs/heads/gdb-head
remote:                         old_rev=2c2cd0d654cc6cf460024feb845ee7ea760290c4
remote:                         new_rev=82f09a220fc59bcdb40896e910bce208c3810b60)
remote: DEBUG: update base: 2c2cd0d654cc6cf460024feb845ee7ea760290c4
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: nowhere@example.com
remote: Subject: [repo/gdb-head] (2 commits) Resync from fsf-master as of today
remote:  (no-precommit-check)
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/gdb-head
remote: X-Git-Oldrev: 2c2cd0d654cc6cf460024feb845ee7ea760290c4
remote: X-Git-Newrev: 82f09a220fc59bcdb40896e910bce208c3810b60
remote:
remote: The branch 'gdb-head' was updated to point to:
remote:
remote:  82f09a2... Resync from fsf-master as of today (no-precommit-check)
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
remote:   82f09a2... Resync from fsf-master as of today (no-precommit-check)
remote:   6a9155b... 2016 copyright header yearly update. (*)
remote:
remote: (*) This commit exists in a branch whose name matches
remote:     the hooks.noemail config option. No separate email
remote:     sent.
remote:
remote: commit 82f09a220fc59bcdb40896e910bce208c3810b60
remote: Merge: 2c2cd0d 6a9155b
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Apr 23 19:17:33 2016 -0400
remote:
remote:     Resync from fsf-master as of today (no-precommit-check)
remote:
remote: commit 6a9155bcd8882eda829932d5b2f7630a32ff9d1e
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Apr 23 19:16:57 2016 -0400
remote:
remote:     2016 copyright header yearly update.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: nowhere@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo/gdb-head] Resync from fsf-master as of today
remote:  (no-precommit-check)
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/gdb-head
remote: X-Git-Oldrev: 2c2cd0d654cc6cf460024feb845ee7ea760290c4
remote: X-Git-Newrev: 82f09a220fc59bcdb40896e910bce208c3810b60
remote:
remote: commit 82f09a220fc59bcdb40896e910bce208c3810b60
remote: Merge: 2c2cd0d 6a9155b
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat Apr 23 19:17:33 2016 -0400
remote:
remote:     Resync from fsf-master as of today (no-precommit-check)
remote:
remote: Diff:
remote:
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
   2c2cd0d..82f09a2  gdb-head -> gdb-head
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
