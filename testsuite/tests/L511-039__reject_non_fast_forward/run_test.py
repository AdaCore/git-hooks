from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try non-fast-forward push on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = testcase.run('git push origin master'.split())
        expected_out = """\
To ../bare/repo.git
 ! [rejected]        master -> master (non-fast-forward)
error: failed to push some refs to '../bare/repo.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. Integrate the remote changes (e.g.
hint: 'git pull ...') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
"""

        if testcase.git_version() < '1.9':
            # Slight differences in output...
            expected_out="""\
To ../bare/repo.git
 ! [rejected]        master -> master (non-fast-forward)
error: failed to push some refs to '../bare/repo.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. Merge the remote changes (e.g. 'git pull')
hint: before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
"""

        assert p.status != 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
