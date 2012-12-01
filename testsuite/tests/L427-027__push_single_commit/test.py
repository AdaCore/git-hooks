from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())

        self.assertTrue(p.status == 0, p.image)

        expected_out = """\
remote: *** cvs_check: `trunk/repo/a'
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
   d065089..a605403  master -> master
"""

        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
