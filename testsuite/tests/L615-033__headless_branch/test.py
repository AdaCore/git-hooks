from support import *

class TestRun(TestCase):
    def test_push(self):
        """Try pushing head-less branch (called "headless") on master.
        Same with head-less branch (called "one-commit") on master.
        The test with the "one-commit" branch is just to test the
        situation where the new head-less branch only has one commit.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debugs to verify that the hooks pick the correct
        # commit as the first commit.
        self.set_debug_level(1)

        # First, push the headless branch.

        p = Run('git push origin headless'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/headless, 0000000000000000000000000000000000000000, 902092ffe1cf61b28e28c86949a447b9fc2591a4)
remote: DEBUG: update base: None
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=None, new_rev=27ebebdd36a485235982f54e8ae68dfea6432c87)
remote: DEBUG: check_commit: old_rev -> 4b825dc642cb6eb9a060e54bf8d69288fbee4904 (empty tree SHA1)
remote: *** cvs_check: `trunk/repo/that.txt'
remote: *** cvs_check: `trunk/repo/this.txt'
remote: DEBUG: check_commit(old_rev=27ebebdd36a485235982f54e8ae68dfea6432c87, new_rev=6586d1c0db5147a521975c15cc6bfd92d2f66de6)
remote: *** cvs_check: `trunk/repo/that.txt'
remote: *** cvs_check: `trunk/repo/there'
remote: DEBUG: check_commit(old_rev=6586d1c0db5147a521975c15cc6bfd92d2f66de6, new_rev=902092ffe1cf61b28e28c86949a447b9fc2591a4)
remote: *** cvs_check: `trunk/repo/this.txt'
remote: DEBUG: post_receive_one(ref_name=0000000000000000000000000000000000000000
remote:                         old_rev=902092ffe1cf61b28e28c86949a447b9fc2591a4
remote:                         new_rev=refs/heads/headless)
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
 * [new branch]      headless -> headless
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

        # Next, push the one-commit branch.

        p = Run('git push origin one-commit'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/one-commit, 0000000000000000000000000000000000000000, ef3ab848df2bef804d5bd0880475d40cb6aab0bf)
remote: DEBUG: update base: None
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=None, new_rev=ef3ab848df2bef804d5bd0880475d40cb6aab0bf)
remote: DEBUG: check_commit: old_rev -> 4b825dc642cb6eb9a060e54bf8d69288fbee4904 (empty tree SHA1)
remote: *** cvs_check: `trunk/repo/contents.txt'
remote: *** cvs_check: `trunk/repo/stuff'
remote: DEBUG: post_receive_one(ref_name=0000000000000000000000000000000000000000
remote:                         old_rev=ef3ab848df2bef804d5bd0880475d40cb6aab0bf
remote:                         new_rev=refs/heads/one-commit)
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
 * [new branch]      one-commit -> one-commit
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
