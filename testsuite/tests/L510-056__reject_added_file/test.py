from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multi-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())

        # The push should fail, because the pre-commit checker will
        # refuse one of the updates.
        self.assertTrue(p.status != 0, ex_run_image(p))

        expected_out = (
            r".*cvs_check: `trunk/repo/b'" +
            r".*cvs_check: `trunk/repo/pck.adb'" +
            r".*pre-commit check failed for file `pck.ads' at commit: " +
                "16c509ed1a0f8b558f8ed9664a06b8cf905fc6b2" +
            r".*cvs_check: `trunk/repo/pck.ads'" +
            r".*ERROR: style-check error detected for file: " +
                r"`trunk/repo/pck\.ads'\." +
            r".*ERROR: Copyright year in header is not up to date" +
            r".*error: hook declined to update refs/heads/master" +
            r".*! \[remote rejected\] master -> master \(hook declined\)" +
            r".*error: failed to push some refs to '\.\./bare/repo.git'")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
