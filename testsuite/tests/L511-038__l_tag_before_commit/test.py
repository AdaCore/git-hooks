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
        # in his repo. Then created a lightweight tag (release-0.1a).
        # Next, he pushes the lightweight tag before having pushed his
        # new commit.
        #
        # Note: The remote repository has been configured to allow
        # unnanotated tags.

        p = Run('git push origin version-0.1a'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/tags/version-0.1a, 0000000000000000000000000000000000000000, 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=426fba3571947f6de7f967e885a3168b9df7004a, new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: *** cvs_check: `trunk/repo/a'
remote: *** cvs_check: `trunk/repo/b'
remote: *** cvs_check: `trunk/repo/c'
remote: DEBUG: post_receive_one(ref_name=refs/tags/version-0.1a
remote:                         old_rev=0000000000000000000000000000000000000000
remote:                         new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
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
remote: X-Git-Newrev: 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote:
remote: The lightweight tag 'version-0.1a' was created pointing to:
remote:
remote:  4f0f08f... Minor modifications.
To ../bare/repo.git
 * [new tag]         version-0.1a -> version-0.1a
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

        # Next, push the changes. Make sure that the commit gets checked.
        # ??? There is a limitation that causes the hooks to re-check
        # a commit which is not new (accessible throught the tag created
        # above, but not from any of the branches).

        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 426fba3571947f6de7f967e885a3168b9df7004a, 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=426fba3571947f6de7f967e885a3168b9df7004a, new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: *** cvs_check: `trunk/repo/a'
remote: *** cvs_check: `trunk/repo/b'
remote: *** cvs_check: `trunk/repo/c'
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=426fba3571947f6de7f967e885a3168b9df7004a
remote:                         new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
   426fba3..4f0f08f  master -> master
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
