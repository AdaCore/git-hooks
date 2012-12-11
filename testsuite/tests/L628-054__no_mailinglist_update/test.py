from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())

        expected_out = """\
remote: *** cvs_check: `trunk/repo/a'
remote: ------------------------------------------------------------
remote: -- WARNING:
remote: -- The hooks.mailinglist config variable not set.
remote: -- Commit emails will only be sent to file-ci@gnat.com.
remote: ------------------------------------------------------------
To ../bare/repo.git
   d065089..a605403  master -> master
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
