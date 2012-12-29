from support import *
import errno
import os
from StringIO import StringIO

# Replace the real os.fork by our own function for unit-test purposes.
# Our function is controlled via a global variable, which is a list
# of booleans. To each boolean corresponds a call to fork, and
# determines whether we want that call to succeed (calling the real
# fork in the process), or fail, raising OSError.
#
# For instance, if good_forks is set to [True, False, True], then
# the first call to os.fork will call the real fork (and hopefully
# succeed), then the second one will raise OSError, and finally,
# the third one will call the real fork again.
#
# The good_forks list is reduced as os.fork gets called.

real_fork = os.fork
good_forks = []


def utest_fork():
    global good_forks
    good_fork = good_forks.pop(0)
    if good_fork:
        pid = real_fork()
        return pid
    else:
        raise OSError(errno.ENOMEM,
                      'fork: Resource temporarily unavailable')


# A small function to use as argument for run_in_daemon.
def hello_world():
    print "Hello World!"


class TestRun(TestCase):
    __real_stdout = sys.stdout
    __real_stderr = sys.stderr

    @classmethod
    def redirect_output(cls):
        sys.stdout = StringIO()
        sys.stderr = sys.stdout

    @classmethod
    def restore_output(cls):
        sys.stdout.close()
        sys.stdout = cls.__real_stdout
        sys.stderr = cls.__real_stderr

    def setUp(self):
        TestCase.setUp(self)
        self.enable_unit_test()

    def test_fail_at_first_fork(self):
        """run_in_daemon fails at first fork...
        """
        from daemon import run_in_daemon
        global good_forks
        good_forks = [False]

        self.redirect_output()
        run_in_daemon(hello_world)
        expected_out = """\
fork #1 failed: (12) fork: Resource temporarily unavailable
"""
        out = sys.stdout.getvalue()
        self.restore_output()

        self.assertEqual(out, expected_out)

    def test_fail_at_second_fork(self):
        """run_in_daemon fails at second fork...
        """
        from daemon import run_in_daemon
        # (we need the third one to work, because fork is used to call
        # the logger).
        global good_forks
        good_forks = [True, False, True]

        self.redirect_output()
        run_in_daemon(hello_world)
        # Not exactly sure why we do not get the output from
        # the logger, but might be normal???
        expected_out = """\
"""
        out = sys.stdout.getvalue()
        self.restore_output()

        self.assertEqual(out, expected_out, out)


if __name__ == '__main__':
    # Redirect fork, allowing us to control its behavior.
    os.fork = utest_fork
    runtests()
