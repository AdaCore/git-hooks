from support import *

class TestRun(TestCase):
    def test_push(testcase):
        """Try pushing branches with bad merges...
        """
        cd ('%s/repo' % TEST_DIR)

        # Try pushing "master".
        #
        # It contains a merge commit whose RH is the default RH
        # for merge commits.  The hooks should reject it.
        p = testcase.run('git push origin master'.split())
        expected_out = """\
remote: *** Pattern "Merge branch '.*'" has been detected.
remote: *** (in commit 3c799a3825af79b1a0f56b00ccc72a1e2837b4ed)
remote: ***
remote: *** This usually indicates an unintentional merge commit.
remote: *** If you would really like to push a merge commit, please
remote: *** edit the merge commit's revision history.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        # Try pushing "master2".
        #
        # This time, it contains a merge commit whose revision
        # history was edited as expected, but the user forgot
        # to remove the "Conflicts:" section.
        p = testcase.run('git push origin master2'.split())
        expected_out = """\
remote: *** Pattern "Conflicts:" has been detected.
remote: *** (in commit 2c7f984bac68db52f1f14cc312509c7242686390)
remote: ***
remote: *** This usually indicates a merge commit where some merge conflicts
remote: *** had to be resolved, but where the "Conflicts:" section has not
remote: *** been deleted from the revision history.
remote: ***
remote: *** Please edit the commit's revision history to either delete
remote: *** the section, or to avoid using the pattern above by itself.
remote: error: hook declined to update refs/heads/master2
To ../bare/repo.git
 ! [remote rejected] master2 -> master2 (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
