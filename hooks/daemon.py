"""A module to handle daemonization...
"""

from __future__ import print_function
import os
import sys
from syslog import syslog


def daemonize(output_fd=None):
    """Create a daemon process.

    PARAMETERS
        output_fd: If not none, a file descriptor where stdout and
            stderr should be redirected.

    RETURN VALUE
        This function returns True for the child (daemon) process,
        while it returns False for the parent process.
    """
    # Perform the first fork.
    try:
        pid = os.fork()
        if pid > 0:
            # In the parent.  We can now return.
            return False
    except OSError as e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        return False

    # Decouple ourselves from the parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()

    # Perform the second fork, to daemonize ourselves.
    try:
        pid = os.fork()
        if pid > 0:
            # In the second parent. Exit.
            sys.exit(0)
    except OSError as e:
        syslog("git-hooks: fork #2 failed: (%d) %s" % (e.errno, e.strerror))
        sys.exit(1)

    # Flush the output...
    for f in sys.stdout, sys.stderr:
        f.flush()

    # Perform the input/output redirection.

    os.close(0)
    os.dup2(os.open('/dev/null', os.O_RDONLY), 0)

    if output_fd is None:  # pragma: no cover (never true in testsuite mode)
        output_fd = os.open('/dev/null', os.O_WRONLY)
    os.close(1)
    os.dup2(output_fd, 1)
    os.close(2)
    os.dup2(output_fd, 2)

    return True


def run_in_daemon(fun):
    """Run the given callbable in a daemon process.

    In GIT_HOOKS_TESTSUITE_MODE, the function's stdout and stderr
    is redirected to a pipe and then re-printed on our stdout.
    But this is only for testing purposes.  In normal mode,
    the function's stdout/stderr, as well as stdin are redirected
    to /dev/null.

    PARAMETERS
        fun: A callable.
    """
    daemon_pipe = (None, None)
    if 'GIT_HOOKS_TESTSUITE_MODE' in os.environ:
        daemon_pipe = os.pipe()

    in_daemon = daemonize(daemon_pipe[1])
    if in_daemon:
        fun()
        sys.exit(0)
    else:
        if daemon_pipe[0] is not None:
            os.close(daemon_pipe[1])
            daemon_stdout = os.fdopen(daemon_pipe[0])
            print(daemon_stdout.read(), file=sys.stderr, end='')
            daemon_stdout.close()
