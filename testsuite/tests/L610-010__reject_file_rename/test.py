from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.

        The commit contains one file rename, but we tell the hooks
        to treat renames as a new file, and thus expect to apply
        the pre-commit checks on the new file.
        """
        cd ('%s/repo' % TEST_DIR)

        os.environ['GIT_HOOKS_DEBUG_LEVEL'] = '2'

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())

        self.assertTrue(p.status != 0, ex_run_image(p))

        expected_out = (
            r".*DEBUG: deleted file ignored: a" +
            r".*pre-commit check failed for file `b' at commit: " +
                "6a48cdab9b100506a387a8398af4751b33a4bfd0" +
            r".*cvs_check: `trunk/repo/b'" +
            r".*ERROR: style-check error detected\." +
            r".*ERROR: Copyright year in header is not up to date" +
            r".*\[remote rejected\]\s+" +
            r"master\s+->\s+master\s+\(hook declined\)")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
