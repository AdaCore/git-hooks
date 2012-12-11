from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multiple commits on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that each commit gets checked individually.
        self.set_debug_level(1)

        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 426fba3571947f6de7f967e885a3168b9df7004a, dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: (combined style checking)
remote: DEBUG: check_commit(old_rev=426fba3571947f6de7f967e885a3168b9df7004a, new_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: *** cvs_check: `trunk/repo/a'
remote: *** cvs_check: `trunk/repo/c'
remote: *** cvs_check: `trunk/repo/d'
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=426fba3571947f6de7f967e885a3168b9df7004a
remote:                         new_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
To ../bare/repo.git
   426fba3..dd6165c  master -> master
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
