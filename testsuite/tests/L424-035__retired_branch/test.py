from support import *

class TestRun(TestCase):
    def test_create_retired_branch(self):
        """Try pushing the (newly-created branch) retired/gdb-5.0.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin retired/gdb-5.0'.split())

        self.assertTrue(p.status == 0, p.image)

        expected_out = """\
remote: *** cvs_check: `trunk/repo/a'
remote: *** email notification for new commits not implemented yet.
To ../bare/repo.git
 * [new branch]      retired/gdb-5.0 -> retired/gdb-5.0
"""

        self.assertEqual(expected_out, p.cmd_out, p.image)


    def test_push_retired_branch(self):
        """Try pushing a branch update on a retired branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin gdb-7.5'.split())

        self.assertTrue(p.status != 0, p.image)

        expected_out = """\
remote: *** Updates to the gdb-7.5 branch are no longer allowed, because
remote: *** this branch has been retired (and renamed into `retired/gdb-7.5').
remote: error: hook declined to update refs/heads/gdb-7.5
To ../bare/repo.git
 ! [remote rejected] gdb-7.5 -> gdb-7.5 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""
        self.assertEqual(expected_out, p.cmd_out, p.image)

    def test_force_push_retired_branch(self):
        """Try force-pushing a branch update on a retired branch.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push -f origin gdb-7.5'.split())

        self.assertTrue(p.status != 0, p.image)

        expected_out = """\
remote: *** Updates to the gdb-7.5 branch are no longer allowed, because
remote: *** this branch has been retired (and renamed into `retired/gdb-7.5').
remote: error: hook declined to update refs/heads/gdb-7.5
To ../bare/repo.git
 ! [remote rejected] gdb-7.5 -> gdb-7.5 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""
        self.assertEqual(expected_out, p.cmd_out, p.image)

    def test_push_retired_branch_as_tag(self):
        """Try pushing a branch update on a retired branch...

        ... where the branch has been marked as retired thanks to
        a tag named retired/<branch-name>
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin gdb-7.6'.split())

        self.assertTrue(p.status != 0, p.image)

        expected_out = """\
remote: *** Updates to the gdb-7.6 branch are no longer allowed, because
remote: *** this branch has been retired (a tag called `retired/gdb-7.6' has been
remote: *** created in its place).
remote: error: hook declined to update refs/heads/gdb-7.6
To ../bare/repo.git
 ! [remote rejected] gdb-7.6 -> gdb-7.6 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""
        self.assertEqual(expected_out, p.cmd_out, p.image)

    def test_force_push_retired_branch_as_tag(self):
        """Try force-pushing a branch update on a retired branch...

        ... where the branch has been marked as retired thanks to
        a tag named retired/<branch-name>
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push -f origin gdb-7.6'.split())

        self.assertTrue(p.status != 0, p.image)

        expected_out = """\
remote: *** Updates to the gdb-7.6 branch are no longer allowed, because
remote: *** this branch has been retired (a tag called `retired/gdb-7.6' has been
remote: *** created in its place).
remote: error: hook declined to update refs/heads/gdb-7.6
To ../bare/repo.git
 ! [remote rejected] gdb-7.6 -> gdb-7.6 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
