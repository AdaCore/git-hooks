from support import *
from shutil import rmtree
import sys
from StringIO import StringIO

class TestRun(TestCase):
    def test_git_config(self):
        """Unit test git_config with invalid config name...
        """
        self.enable_unit_test()

        import utils

        assert utils.scratch_dir is None

        # Call create_scratch_dir, and verify that no warning is printed
        # on stderr, by redirecting it to a StringIO file.
        real_stderr = sys.stderr
        new_stderr = StringIO()

        sys.stderr = new_stderr
        utils.create_scratch_dir()
        sys.stderr = real_stderr

        rmtree(utils.scratch_dir)
        self.assertEqual(new_stderr.getvalue(), "", new_stderr.getvalue())
        new_stderr.close()

        # Call create_scratch_dir again, and verify that a warning is
        # printed, this time.
        new_stderr = StringIO()

        sys.stderr = new_stderr
        utils.create_scratch_dir()
        sys.stderr = real_stderr

        rmtree(utils.scratch_dir)
        assert (
            "Unexpected second call to create_scratch_dir" in new_stderr.getvalue()
        ), new_stderr.getvalue()
        new_stderr.close()


if __name__ == '__main__':
    runtests()
