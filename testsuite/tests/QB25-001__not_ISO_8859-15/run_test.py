# -*- coding: utf8 -*-
from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # For this testcase, the contents of the emails being sent
        # is not important, so reduce their verbosity.
        testcase.change_email_sending_verbosity(full_verbosity=False)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.

        p = testcase.run('git push origin master'.split())
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

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Push bad-after-subject to the `origin' remote as branch master.
        # The delta should be one commit with one file being modified.

        p = testcase.run('git push origin bad-after-subject'.split())
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
remote: error: hook declined to update refs/heads/bad-after-subject
To ../bare/repo.git
 ! [remote rejected] bad-after-subject -> bad-after-subject (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        ##############################################################
        #
        #  Phase 2 of this testcase, let's try to push the branches
        #  above again, but after having configured the repository
        #  to disable the character range check in revision logs.
        #
        ##############################################################

        p = testcase.run('git fetch origin refs/meta/config'.split())
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run('git checkout FETCH_HEAD'.split())
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'config', '-f', 'project.config',
                 '--add', 'hooks.no-rh-character-range-check', 'True'])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run(['git', 'commit',
                 '-m', 'Set hooks.no-rh-character-range-check to True',
                 'project.config'])
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run('git push origin HEAD:refs/meta/config'.split())
        testcase.assertEqual(p.status, 0, p.image)

        p = testcase.run('git checkout master'.split())
        testcase.assertEqual(p.status, 0, p.image)

        # Try pushing branch "master". It should succeed, now.

        p = testcase.run('git push origin master'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: Sending email: =?utf-8?q?=5Brepo=5D_Some_revision_history_with_bad_chars=E2=81=A9?=...
To ../bare/repo.git
   d065089..cee1725  master -> master
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Try pushing branch "bad-after-subject". It should succeed as well.

        p = testcase.run('git push origin bad-after-subject'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `a'
remote: DEBUG: Sending email: [repo/bad-after-subject] This is the subject....
To ../bare/repo.git
   d065089..48f93aa  bad-after-subject -> bad-after-subject
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
