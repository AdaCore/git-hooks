from support import *

class TestRun(TestCase):
    def test_git_config(testcase):
        """Unit test git_config with invalid config name...
        """
        testcase.enable_unit_test()

        from config import git_config, UnsupportedOptionName
        with testcase.assertRaises(UnsupportedOptionName):
            git_config('bad option name')


if __name__ == '__main__':
    runtests()
