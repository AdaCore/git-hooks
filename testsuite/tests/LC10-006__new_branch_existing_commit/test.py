from support import *

class TestRun(TestCase):
    def test_push_new_branch(self):
        """Try pushing a new branch which creates no new commit at all.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin my-topic'.split())
        expected_out = """\
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
 * [new branch]      my-topic -> my-topic
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
