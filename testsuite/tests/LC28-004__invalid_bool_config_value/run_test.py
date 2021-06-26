from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing one single-file commit on master.

        The purpose of this testcase is to test combined style checking.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The update should
        # fail because hooks.combined-style-checking does not have
        # a valid value (simulating a typo).
        p = testcase.run('git push origin master'.split())
        expected_out = """\
remote: *** Invalid hooks.combined-style-checking value: frue (must be boolean)
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
