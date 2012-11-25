from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multi-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())

        # The push should fail, because the pre-commit checker will
        # refuse one of the updates.
        self.assertTrue(p.status != 0, p.image)

        expected_out = (
            r".*cvs_check: `trunk/repo/a'" +
            r".*pre-commit check failed for file `b' at commit: " +
                "4f0f08f46daf6f5455cf90cdc427443fe3b32fa3" +
            r".*cvs_check: `trunk/repo/b'" +
            r".*ERROR: style-check error detected\." +
            r".*ERROR: Copyright year in header is not up to date" +
            r".*error: hook declined to update refs/heads/master" +
            r".*! \[remote rejected\] master -> master \(hook declined\)" +
            r".*error: failed to push some refs to '\.\./bare/repo.git'")

        self.assertTrue(re.match(expected_out, p.cmd_out, re.DOTALL),
                        p.image)

if __name__ == '__main__':
    runtests()
