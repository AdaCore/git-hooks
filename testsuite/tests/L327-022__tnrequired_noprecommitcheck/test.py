from support import *

class TestRun(TestCase):
    def test_push(self):
        """Test pushing master...
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The should push
        # one merge commit which also references a commit from
        # the thirdparty branch.  It is the commit from thirdparty
        # which has an invalid revision history where a ticket
        # number is missing from the revision history.
        #
        # As the invalid commit is has not been pushed to the remote
        # repository yet, it counts as "new", and thus should be
        # validated through the pre-commit checks, which means
        # that we expect the update to fail.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** The following commit is missing a ticket number inside
remote: *** its revision history.  If the change is sufficiently
remote: *** minor that a ticket number is not meaningful, please use
remote: *** the word "no-tn-check" in place of a ticket number.
remote: ***
remote: *** commit ef602fcf81b53dc7512d6c404c532f5c07187abf
remote: *** Subject: Add second bottom to top.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Now, push the thirdparty branch.  This branch is setup
        # to avoid the pre-commit checks, so this should allow
        # the problematic commit.
        p = Run('git push origin thirdparty'.split())
        expected_out = """\
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/heads/thirdparty',
remote: --  which matches the name of the reference being updated
remote: --  (refs/heads/thirdparty).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
   52723db..ef602fc  thirdparty -> thirdparty
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # And finally, try pushing the "master" branch again.
        # This time, the problematic commit is already in, and
        # so should not go through the pre-commit-checks again.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `top'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] (2 commits) Merge the changes made in the 'thirdparty' branch.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 96cc4826ed3f82bee77514177ff3944601d1800d
remote: X-Git-Newrev: 3c75c8d4c196c09cae03ba1832b4c31285f8a85e
remote:
remote: The branch 'master' was updated to point to:
remote:
remote:  3c75c8d... Merge the changes made in the 'thirdparty' branch.
remote:
remote: It previously pointed to:
remote:
remote:  96cc482... Add end to top.
remote:
remote: Diff:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   3c75c8d... Merge the changes made in the 'thirdparty' branch.
remote:   ef602fc... Add second bottom to top. (*)
remote:
remote: (*) This commit exists in a branch whose name matches
remote:     the hooks.noemail config option. No separate email
remote:     sent.
remote:
remote: commit 3c75c8d4c196c09cae03ba1832b4c31285f8a85e
remote: Merge: 96cc482 ef602fc
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Dec 26 11:13:44 2012 +0400
remote:
remote:     Merge the changes made in the 'thirdparty' branch.
remote:
remote:     This repo requires a ticket number, so there: L327-022.
remote:
remote: commit ef602fcf81b53dc7512d6c404c532f5c07187abf
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu Dec 20 21:51:00 2012 +0400
remote:
remote:     Add second bottom to top.
remote:
remote:     This commit comes from an external source, and thus does not have
remote:     a ticket number in the rh.  But that's OK, because it is on a branch
remote:     for which pre-commit-checks are disabled.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Merge the changes made in the 'thirdparty' branch.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 96cc4826ed3f82bee77514177ff3944601d1800d
remote: X-Git-Newrev: 3c75c8d4c196c09cae03ba1832b4c31285f8a85e
remote:
remote: commit 3c75c8d4c196c09cae03ba1832b4c31285f8a85e
remote: Merge: 96cc482 ef602fc
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Dec 26 11:13:44 2012 +0400
remote:
remote:     Merge the changes made in the 'thirdparty' branch.
remote:
remote:     This repo requires a ticket number, so there: L327-022.
remote:
remote: Diff:
remote:
remote:  top | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --cc top
remote: index 474616d,f2a80be..7373737
remote: --- a/top
remote: +++ b/top
remote: @@@ -1,4 -1,4 +1,5 @@@
remote:   Top
remote:   Middle
remote:   Bottom
remote: + Additional Bottom.
remote:  +End.
To ../bare/repo.git
   96cc482..3c75c8d  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
