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
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Created branch retired/gdb-5.0
remote: X-ACT-checkin: repo
remote: X-Git-Refname: refs/heads/retired/gdb-5.0
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7
remote:
remote: The branch 'retired/gdb-5.0' was created pointing to:
remote:
remote:  a605403... Updated a.
remote:
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
