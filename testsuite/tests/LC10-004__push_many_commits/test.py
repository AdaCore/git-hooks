from support import *

class TestRun(TestCase):
    def test_push_too_many_new_commits_on_master(self):
        """Try pushing too many new commits on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The remote should
        # reject it saying that there are too many new commits.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: ---------------------------------------------------------------------------
remote: --  The hooks.no-emails config parameter contains `refs/heads/master'.
remote: --  Commit emails will therefore not be sent.
remote: ---------------------------------------------------------------------------
To ../bare/repo.git
   d065089..4ca9852  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
