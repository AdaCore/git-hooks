from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(testcase):
        """Try non-fast-forward push on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push -f origin master'.split())
        expected_out = """\
remote: *** Non-fast-forward updates are not allowed for this reference.
remote: *** Please rebase your changes on top of the latest HEAD,
remote: *** and then try pushing again.
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] master -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        assert p.status != 0, p.image
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
