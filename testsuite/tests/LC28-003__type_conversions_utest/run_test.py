from support import *


class TestRun(TestCase):
    def test_get_user_name(testcase):
        """Unit test utils.get_user_name."""
        testcase.run_unit_test_script(
            expected_out="""\
True
False
"""
        )


if __name__ == "__main__":
    runtests()
