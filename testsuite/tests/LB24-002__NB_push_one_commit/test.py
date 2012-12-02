from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multi-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** cvs_check: `trunk/repo/a'
remote: *** cvs_check: `trunk/repo/b'
remote: *** cvs_check: `trunk/repo/c'
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
   426fba3..4f0f08f  master -> master
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
