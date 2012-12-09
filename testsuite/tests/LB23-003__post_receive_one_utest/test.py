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

        # No need to pass a valid EmailInfo, so pass None instead.
        post_receive_one(
            'bogus/heads/master',
            '0000000000000000000000000000000000000000',
            'd065089ff184d97934c010ccd0e7e8ed94cb7165',
            None, None)
        expected_out = """\
*** post-receive: Unsupported reference update: bogus/heads/master (ignored).
***               old_rev = 0000000000000000000000000000000000000000
***               new_rev = d065089ff184d97934c010ccd0e7e8ed94cb7165
"""
        self.assertEqual(sys.stderr.getvalue(), expected_out)

        # Restore sys.stderr...
        sys.stderr = old_stderr


if __name__ == '__main__':
    runtests()
