from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multiple commits on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `a'
remote: *** cvs_check: `repo' < `b'
remote: *** cvs_check: `repo' < `c'
remote: *** cvs_check: `repo' < `c'
remote: *** cvs_check: `repo' < `d'
remote: *** cvs_check: `repo' < `c'
remote: *** cvs_check: `repo' < `d'
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/heads/mas.*',
remote: --  which matches the name of the reference being updated
remote: --  (refs/heads/master).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
   426fba3..dd6165c  master -> master
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
