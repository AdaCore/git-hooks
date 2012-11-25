from support import *
import os

class TestRun(TestCase):
    def test_push(self):
        """Try pushing one single-file commit on master.

        The operation should fail due to either config.debuglevel
        having an invalid value, or GIT_HOOKS_DEBUG_LEVEL having
        an invalid value.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.
        p = Run('git push origin master'.split())

        self.assertTrue(p.status != 0, ex_run_image(p))

        expected_out = (
            r".*Invalid hooks\.debuglevel value: -1" +
            r".*! \[remote rejected\]\s+master\s+->\s+master\s+" +
                r"\(hook declined\)")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

        # Same thing, but with an invalid GIT_HOOKS_DEBUG_LEVEL value.
        self.set_debug_level('true')

        p = Run('git push origin master'.split())

        self.assertTrue(p.status != 0, ex_run_image(p))

        expected_out = (
            r".*Invalid value for GIT_HOOKS_DEBUG_LEVEL: true" +
            r".*! \[remote rejected\]\s+master\s+->\s+master\s+" +
                r"\(hook declined\)")

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))


if __name__ == '__main__':
    runtests()
