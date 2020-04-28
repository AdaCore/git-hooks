from support import *
from StringIO import StringIO
import sys


class TestRun(TestCase):
    def test_post_receive_one(self):
        """Unit test utils.get_user_name.
        """
        self.enable_unit_test()

        # Redirect stdout in order to capture it, and check its contents.
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        from post_receive import post_receive_one

        post_receive_one(
            'refs/heads/v1',
            '0000000000000000000000000000000000000000',
            '30242ad9fa3091c81e55a7b1349ab83f8c1b04e7',
            None, None)
        expected_out = """\
*** post-receive: Unsupported reference update: refs/heads/v1 (ignored).
***               old_rev = 0000000000000000000000000000000000000000
***               new_rev = 30242ad9fa3091c81e55a7b1349ab83f8c1b04e7
"""
        self.assertEqual(sys.stderr.getvalue(), expected_out)

        # Restore sys.stderr...
        sys.stderr = old_stderr


if __name__ == '__main__':
    runtests()
