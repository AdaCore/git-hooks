from support import *

class TestRun(TestCase):
    def test_empty_line_after_subject(self):
        """Test the rejection of revision histories missing an empty line
        after the commit subject.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable pre-commit-check debug traces...
        self.set_debug_level(1)

        # Push master to the `origin' remote.  The should push
        # one merge commit which also references a commit from
        # the thirdparty branch.  It is the commit from thirdparty
        # which has an invalid revision history where the empty
        # line after the commit subject is missing.
        #
        # As the invalid commit is has not been pushed to the remote
        # repository yet, it counts as "new", and thus should be
        # validated through the pre-commit checks, which means
        # that we expect the update to fail.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 96cc4826ed3f82bee77514177ff3944601d1800d, bd6c0a7343402a7a5d1e5b42e5d338e5c1e3cb35)
remote: DEBUG: update base: 96cc4826ed3f82bee77514177ff3944601d1800d
remote: *** Invalid revision history for commit 492fd2fae27c2f358c1d59c59a2e13ec2a3a880f:
remote: *** The first line should be the subject of the commit,
remote: *** followed by an empty line.
remote: ***
remote: *** Below are the first few lines of the revision history:
remote: *** | Add second bottom to top.
remote: *** | The second line should have been an empty line.
remote: *** | This is very bad, so try to reject the update if detected on
remote: *** | a branch that does not have noprecommitcheck.
remote: ***
remote: *** Please amend the commit's revision history and try again.
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
remote: DEBUG: validate_ref_update (refs/heads/thirdparty, 52723db7f709396057df819f73e66b846858217e, 492fd2fae27c2f358c1d59c59a2e13ec2a3a880f)
remote: DEBUG: (hooks.no-precommit-check match: `refs/heads/thirdparty')
remote: SYSLOG: cvs_check: Pre-commit checks disabled for 492fd2fae27c2f358c1d59c59a2e13ec2a3a880f on repo by hooks.no-precommit-check config (refs/heads/thirdparty)
remote: DEBUG: post_receive_one(ref_name=refs/heads/thirdparty
remote:                         old_rev=52723db7f709396057df819f73e66b846858217e
remote:                         new_rev=492fd2fae27c2f358c1d59c59a2e13ec2a3a880f)
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/heads/thirdparty',
remote: --  which matches the name of the reference being updated
remote: --  (refs/heads/thirdparty).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
   52723db..492fd2f  thirdparty -> thirdparty
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # And finally, try pushing the "master" branch again.
        # This time, the problematic commit is already in, and
        # so should not go through the pre-commit-checks again.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 96cc4826ed3f82bee77514177ff3944601d1800d, bd6c0a7343402a7a5d1e5b42e5d338e5c1e3cb35)
remote: DEBUG: update base: 96cc4826ed3f82bee77514177ff3944601d1800d
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=96cc4826ed3f82bee77514177ff3944601d1800d, new_rev=bd6c0a7343402a7a5d1e5b42e5d338e5c1e3cb35)
remote: *** cvs_check: `trunk/repo/top'
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=96cc4826ed3f82bee77514177ff3944601d1800d
remote:                         new_rev=bd6c0a7343402a7a5d1e5b42e5d338e5c1e3cb35)
remote: DEBUG: update base: 96cc4826ed3f82bee77514177ff3944601d1800d
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] (2 commits) Merge changes from branch thirdparty.
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 96cc4826ed3f82bee77514177ff3944601d1800d
remote: X-Git-Newrev: bd6c0a7343402a7a5d1e5b42e5d338e5c1e3cb35
remote:
remote: The branch 'master' was updated to point to:
remote:
remote:  bd6c0a7... Merge changes from branch thirdparty.
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
remote:   492fd2f... Add second bottom to top. The second line should have been  (*)
remote:   bd6c0a7... Merge changes from branch thirdparty.
remote:
remote: (*) This commit already existed in another branch/reference.
remote:      No separate email sent.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Merge changes from branch thirdparty.
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 96cc4826ed3f82bee77514177ff3944601d1800d
remote: X-Git-Newrev: bd6c0a7343402a7a5d1e5b42e5d338e5c1e3cb35
remote:
remote: commit bd6c0a7343402a7a5d1e5b42e5d338e5c1e3cb35
remote: Merge: 96cc482 492fd2f
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu Dec 20 21:55:52 2012 +0400
remote:
remote:     Merge changes from branch thirdparty.
remote:
remote:     This changs only bring a second bottom to top.
remote:     Nothing else.
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
   96cc482..bd6c0a7  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
