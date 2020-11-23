"""Handling of syslog-ing...
"""

from __future__ import print_function
from os import environ
from subprocess import Popen, PIPE, STDOUT

from utils import warn


def syslog(message, tag='style_checker', priority='local0.warn'):
    """Add the given entry to the syslog file.

    PARAMETERS
        message: The message to file.
        tag: Mark every line in the log with the specified tag.
        priority: Enter the message with the specified priority.
    """
    logger_exe = 'logger'
    if 'GIT_HOOKS_LOGGER' in environ:
        logger_exe = environ['GIT_HOOKS_LOGGER']

    p = Popen([logger_exe, '-t', tag, '-p', priority, message],
              stdout=PIPE, stderr=STDOUT)
    out, _ = p.communicate()
    if p.returncode != 0:
        info = (['Failed to file the following syslog entry:',
                 '  - message: %s' % message,
                 '  - tag: %s' % tag,
                 '  - priority: %s' % priority,
                 '',
                 'logger returned with error code %d:' % p.returncode] +
                out.splitlines())
        warn(*info)

    elif out.rstrip():
        print(out.rstrip())
