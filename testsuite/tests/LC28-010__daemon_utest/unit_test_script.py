import errno
import os

# Import from git-hooks modules...
from daemon import run_in_daemon
from syslog import syslog


# A small function to use as argument for run_in_daemon.
def hello_world():
    print("Hello World!")


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

good_forks = []


def utest_fork():
    global good_forks
    good_fork = good_forks.pop(0)
    if good_fork:
        pid = real_fork()
        return pid
    else:
        raise OSError(errno.ENOMEM, "fork: Resource temporarily unavailable")


real_fork = os.fork
os.fork = utest_fork

print("DEBUG: Test run_in_daemon failing at the first fork...")

good_forks = [False]
run_in_daemon(hello_world)

# FIXME: We would like to test the case where run_in_daemon fails at
# the second fork, but for some reason, this causes problems with
# coverage testing, due to the at_exit handler trying to save coverage
# results in a file located in "/". This daemonize code has been
# pretty much unchanged since it was introduced, so accept not covering
# this part.
#
# print("DEBUG: Test run_in_daemon failing at the second fork...")
#
# # (we need the third one to work, because fork is used to call the logger).
# good_forks = [True, False, True]
#
# run_in_daemon(hello_world)

# FIXME: As the result of the above, one call to syslog where the logger
# returns nonzero is lost, reducing code coverage. Just call it by hand
# from here (after having restored os.fork).
os.fork = real_fork
syslog("my message")
