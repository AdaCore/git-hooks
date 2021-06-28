from support import *


class TestRun(TestCase):
    def test_funtions_in_utils(testcase):
        """Unit test some functions in utils."""
        testcase.run_unit_test_script(
            expected_out="""\
John Smith
"""
        )


if __name__ == "__main__":
    runtests()
