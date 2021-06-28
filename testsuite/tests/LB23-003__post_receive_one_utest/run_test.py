from support import *


class TestRun(TestCase):
    def test_post_receive_one(testcase):
        """Unit test utils.get_user_name."""
        testcase.run_unit_test_script(
            expected_out="""\
*** post-receive: Unsupported reference update: refs/heads/v1 (ignored).
***               old_rev = 0000000000000000000000000000000000000000
***               new_rev = 30242ad9fa3091c81e55a7b1349ab83f8c1b04e7
"""
        )


if __name__ == "__main__":
    runtests()
