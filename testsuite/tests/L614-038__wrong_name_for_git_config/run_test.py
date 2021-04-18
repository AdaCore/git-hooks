from support import *

class TestRun(TestCase):
    def test_git_config(self):
        """Unit test git_config with invalid config name...
        """
        self.enable_unit_test()

        from config import git_config, UnsupportedOptionName
        with self.assertRaises(UnsupportedOptionName):
            git_config('bad option name')


if __name__ == '__main__':
    runtests()
