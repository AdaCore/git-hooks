from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing tag referencing new commit.
        """
        cd ('%s/repo' % TEST_DIR)

        # We need some debug traces to be enabled, in order to verify
        # certain assertions.
        self.set_debug_level(1)

        # Scenario: The user made some changes, and then committed them
        # in his repo. Then created an annotated tag (release-0.1a).
        # Next, he pushes the annotated tag before having pushed his
        # new commit.  What the commit hooks should do in this case
        # is do the same as in a branch update (pre-commit checks,
        # commit emails, etc).

        p = Run('git push origin version-0.1a'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/tags/version-0.1a, 0000000000000000000000000000000000000000, b03c3952e1cd29c6ec0cad2590689c0b22d02197)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=426fba3571947f6de7f967e885a3168b9df7004a, new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: *** cvs_check: `trunk/repo/a'
remote: *** cvs_check: `trunk/repo/b'
remote: *** cvs_check: `trunk/repo/c'
remote: DEBUG: post_receive_one(ref_name=refs/tags/version-0.1a
remote:                         old_rev=0000000000000000000000000000000000000000
remote:                         new_rev=b03c3952e1cd29c6ec0cad2590689c0b22d02197)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Created tag version-0.1a
remote: X-ACT-checkin: repo
remote: X-Git-Refname: refs/tags/version-0.1a
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: b03c3952e1cd29c6ec0cad2590689c0b22d02197
remote:
remote: The unsigned tag 'version-0.1a' was created pointing to:
remote:
remote:  4f0f08f... Minor modifications.
remote:
remote: Tagger: Joel Brobecker <brobecker@adacore.com>
remote: Date: Fri May 11 15:56:32 2012 -0700
remote:
remote:     Tag version 0.1 alpha.
remote:
remote:     First (alpha) release of this project.
To ../bare/repo.git
 * [new tag]         version-0.1a -> version-0.1a
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

        # Next, push the changes.  The commits are no longer "new",
        # and thus nothing other than the reference change should
        # be done.

        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 426fba3571947f6de7f967e885a3168b9df7004a, 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=426fba3571947f6de7f967e885a3168b9df7004a
remote:                         new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Minor modifications.
remote: X-ACT-checkin: repo
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 426fba3571947f6de7f967e885a3168b9df7004a
remote: X-Git-Newrev: 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote:
remote: The branch 'master' was updated to point to:
remote:
remote:  4f0f08f... Minor modifications.
remote:
remote: It previously pointed to:
remote:
remote:  426fba3... Initial commit.
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   4f0f08f... Minor modifications. (*)
remote:
remote: (*) This commit already existed in another branch/reference.
remote:      No separate email sent.
To ../bare/repo.git
   426fba3..4f0f08f  master -> master
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
