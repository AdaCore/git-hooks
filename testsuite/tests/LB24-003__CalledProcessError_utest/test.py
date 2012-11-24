from support import *

class TestRun(TestCase):
    def test_called_process_error_str_method(self):
        """Unit test git.CalledProcessError.__str__.
        """
        self.enable_unit_test()

        from git import git, CalledProcessError

        # Perform a git operation that we know will cause an error.
        # For instance, try to checkout a branch (and use an invalid
        # branch name for good measure).
        with self.assertRaisesRegexp(
            CalledProcessError,
            "Command 'git checkout foobar' returned non-zero exit status"):
            git.checkout('foobar', _quiet=True)


if __name__ == '__main__':
    runtests()
