from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing multiple commits on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that each commit gets checked individually.
        testcase.set_debug_level(1)

        p = testcase.run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 426fba3571947f6de7f967e885a3168b9df7004a, dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: style_check_commit(old_rev=426fba3571947f6de7f967e885a3168b9df7004a, new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: *** cvs_check: `repo' < `a' `b' `c'
remote: DEBUG: style_check_commit(old_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3, new_rev=4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf)
remote: *** cvs_check: `repo' < `c' `d'
remote: DEBUG: style_check_commit(old_rev=4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf, new_rev=cc8d2c2637bda27f0bc2125181dd2f8534d16222)
remote: *** cvs_check: `repo' < `c'
remote: DEBUG: style_check_commit(old_rev=cc8d2c2637bda27f0bc2125181dd2f8534d16222, new_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: *** cvs_check: `repo' < `d'
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=426fba3571947f6de7f967e885a3168b9df7004a
remote:                         new_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/heads/master',
remote: --  which matches the name of the reference being updated
remote: --  (refs/heads/master).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
   426fba3..dd6165c  master -> master
"""

        assert p.status == 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
