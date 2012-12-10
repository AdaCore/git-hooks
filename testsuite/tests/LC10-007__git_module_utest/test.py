from support import *

class TestRun(TestCase):
    def test_git_config(self):
        """Unit test AbstractUpdate child class missing methods.
        """
        self.enable_unit_test()


        from git import git

        cd ('%s/repo' % TEST_DIR)

        # Test the git --switch=False attribute.
        out = git.log('-n1', pretty='format:%P').strip()
        self.assertEqual(out, 'd065089ff184d97934c010ccd0e7e8ed94cb7165')


if __name__ == '__main__':
    runtests()
