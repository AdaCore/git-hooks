"""Handling of syslog-ing...
"""

from gnatpython.ex import Run
from os import environ
from utils import warn


def syslog(message, tag='cvs_check', priority='local0.warn'):
    """Add the given entry to the syslog file.

    PARAMETERS
        message: The message to file.
        tag: Mark every line in the log with the specified tag.
        priority: Enter the message with the specified priority.
    """
    logger_exe = 'logger'
    if 'GIT_HOOKS_LOGGER' in environ:
        logger_exe = environ['GIT_HOOKS_LOGGER']

    p = Run([logger_exe, '-t', tag, '-p', priority, message])
    if p.status != 0:
        info = (['Failed to file the following syslog entry:',
                 '  - message: %s' % message,
                 '  - tag: %s' % tag,
                 '  - priority: %s' % priority,
                 '',
                 'logger returned with error code %d:' % p.status]
                + p.out.splitlines())
        warn(*info)

    elif p.out.rstrip():
        print p.out.rstrip()
