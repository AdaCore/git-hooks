from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing master...
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** The following commit is missing a ticket number inside
remote: *** its revision history.  If the change is sufficiently
remote: *** minor that a ticket number is not meaningful, please use
remote: *** either the word "Minor" or the "(no-tn-check)" string
remote: *** in place of a ticket number.
remote: ***
remote: *** commit a60540361d47901d3fe254271779f380d94645f7
remote: *** Subject: Updated a.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertEqual(expected_out, p.cmd_out, p.image)

if __name__ == '__main__':
    runtests()
