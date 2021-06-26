from support import *

class TestRun(TestCase):
    def test_delete_meta_config(testcase):
        """Try deleting the refs/meta/config branch (not allowed)
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin :refs/meta/config'.split())
        expected_out = """\
remote: *** Deleting the reference refs/meta/config is not allowed.
remote: ***
remote: *** This reference provides important configuration information
remote: *** and thus must not be deleted.
To ../bare/repo.git
 ! [remote rejected] refs/meta/config (pre-receive hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
