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
remote: *** This update introduces too many new commits (4), which would
remote: *** trigger as many emails, exceeding the current limit (3).
remote: *** Contact your repository adminstrator if you really meant
remote: *** to generate this many commit emails.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertTrue(p.status != 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

        # Now, try pushing only HEAD~, which should only push
        # 3 new commits, which should be under the limit, and
        # thus be accepted.
        p = Run('git push origin master~:master'.split())
        expected_out = """\
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
   d065089..c32bed0  master~ -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

        # Now, try push master again.  We should have one last
        # new commit left to push...
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
   c32bed0..4ca9852  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)


if __name__ == '__main__':
    runtests()
