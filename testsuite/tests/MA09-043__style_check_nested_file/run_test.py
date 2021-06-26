from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = testcase.run('git push origin master'.split())
        expected_out = """\
remote: *** pre-commit check failed for commit: d402899ac1ae2b5896c2b1558cdf1564ffa54d01
remote: *** cvs_check: `repo' < `path/to/file'
remote: *** File `path/to/file' contains:
remote: *** New file.
remote: *** A second line.
remote: ***
remote: *** --- Done ---
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertEqual(p.status, 1, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
