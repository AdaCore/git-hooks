from os import environ
import sys

from config import git_config

class InvalidUpdate(Exception):
    """An exception raised when the update is not accepted.
    """
    pass


def debug(msg):
    """Print a debug message on stdout if debug traces are turned on.

    To turn debug traces on, set the HOOKS_DEBUG environment variable,
    or set the hooks.debug config variable to "true".

    PARAMETERS
        msg: The debug message to be printed.  The message will be
            prefixed with "DEBUG: ".
    """
    if ('HOOKS_DEBUG' in environ or git_config('hooks.debug') == 'true'):
        warn(msg, prefix='DEBUG:')


def warn(*args, **kwargs):
    """Print the given args on stderr, prefixed with the given prefix.

    All messages that needs to be printed and then relayed back to
    the user should go through this function, because we want to make
    sure that they are printed using a consistent style.

    We also want to make sure that they are all sent to the same file
    descriptor, to make sure that all messages are relayed to back to
    the user in the correct order.  Otherwise, the messages sent to
    stderr are all printed before the messages sent to stdout.

    PARAMETERS
        *args: Zero or more arguments to be printed on stderr.
        prefix: The prefix to be used when printing the message.
            Default value is '***'.
    """
    prefix = kwargs['prefix'] if 'prefix' in kwargs else '***'
    for arg in args:
        print >> sys.stderr, prefix , arg

