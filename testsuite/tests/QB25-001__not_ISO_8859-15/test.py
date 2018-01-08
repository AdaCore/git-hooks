# -*- coding: utf8 -*-
from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** Invalid revision history for commit cee1725c0a285a6e13bbb4536f44f097b6773783:
remote: *** It contains characters not in the ISO-8859-15 charset.
remote: ***
remote: *** Below is the first line where this was detected (line 1):
remote: *** | Some revision history with bad chars⁩
remote: ***                                       ^
remote: ***                                       |
remote: ***
remote: *** Please amend the commit's revision history to remove it
remote: *** and try again.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

    def test_push_bad_after_subject(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push bad-after-subject to the `origin' remote as branch master.
        # The delta should be one commit with one file being modified.
        p = Run('git push origin bad-after-subject:master'.split())
        expected_out = """\
remote: *** Invalid revision history for commit 48f93aa312e5ae8b64589492730e4ee318368d7f:
remote: *** It contains characters not in the ISO-8859-15 charset.
remote: ***
remote: *** Below is the first line where this was detected (line 3):
remote: *** | Some revision history with bad chars⁩
remote: ***                                       ^
remote: ***                                       |
remote: ***
remote: *** Please amend the commit's revision history to remove it
remote: *** and try again.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] bad-after-subject -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
