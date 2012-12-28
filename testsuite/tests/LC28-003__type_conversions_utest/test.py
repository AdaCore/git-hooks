from support import *


class TestRun(TestCase):
    def test_get_user_name(self):
        """Unit test utils.get_user_name.
        """
        self.enable_unit_test()

        from type_conversions import to_bool

        # The purpose of this test is to test that do coverage
        # testing of the case where to_bool is called with
        # a boolean value.
        self.assertEqual(to_bool(True), True)
        self.assertEqual(to_bool(False), False)


if __name__ == '__main__':
    runtests()
