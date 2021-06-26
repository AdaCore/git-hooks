from support import *

class TestRun(TestCase):
    def test_get_user_name(testcase):
        """Unit test utils.get_user_name.
        """
        testcase.enable_unit_test()

        from utils import get_user_name

        # Just make sure the function returns something when
        # GIT_HOOKS_USER_NAME does not exist.
        del(os.environ['GIT_HOOKS_USER_NAME'])
        testcase.assertIsNotNone(get_user_name())

    def test_get_user_full_name(testcase):
        """Unit test utils.get_user_full_name."""
        testcase.enable_unit_test()

        from utils import get_user_full_name

        # Just make sure the function returns something.
        del(os.environ['GIT_HOOKS_USER_FULL_NAME'])
        testcase.assertIsNotNone(get_user_full_name())

        # Try the case where the user full name contains
        # and email address.
        os.environ['GIT_HOOKS_USER_FULL_NAME'] = \
            'John Smith  <j.smith@example.com> '
        testcase.assertEqual(get_user_full_name(),
                         'John Smith')


if __name__ == '__main__':
    runtests()
