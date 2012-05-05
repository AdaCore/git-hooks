from os import environ
import sys
from tempfile import mkdtemp

from config import git_config

class InvalidUpdate(Exception):
    """An exception raised when the update is not accepted.
    """
    pass

############################################################################
#
#  Temporary directory handling.
#
############################################################################
#
# The idea is to create a temporary directory at the start of the
# session, and to delete it at the end.

scratch_dir = None

def create_scratch_dir():
    """Create a temporary directory.

    Set scratch_dir to the name of that new directory.
    """
    global scratch_dir
    if scratch_dir is not None:
        warn('Unexpected second call to create_scratch_dir')
    scratch_dir = mkdtemp('', 'git-hooks-tmp-')


############################################################################
#
# Warning messages, error message, debug traces, etc...
#
############################################################################

def debug(msg, level=1):
    """Print a debug message on stderr if appropriate.

    The debug trace is generated if the debug level is greater or
    equal to the given trace priority.

    The debug level is an integer value which can be changed either
    by setting the `HOOKS_DEBUG_LEVEL' environment variable, or else
    by setting the hooks.debuglevel git config value.  The value
    must be an integer value, or this function raises InvalidUpdate.
    By default, the debug level is set to zero (no debug traces).


    PARAMETERS
        msg: The debug message to be printed.  The message will be
            prefixed with "DEBUG: " (an indentation proportional to
            the level will be used).
        level: The trace level. The smaller the number, the important
            the trace message. Traces that are repetitive, or part
            of a possibly large loop, or less important, should use
            a value that is higher than 1.

    REMARKS
        Raising InvalidUpdate for an invalid debug level value is
        a little abusive.  But it simplifies a bit the update script,
        which then only has to handle a single exception...
    """
    if 'HOOKS_DEBUG_LEVEL' in environ:
        debug_level = environ['HOOKS_DEBUG_LEVEL']
        if not debug_level.isdigit():
            raise InvalidUpdate('Invalid value for HOOKS_DEBUG_LEVEL: %s '
                                '(must be integer >= 0)')
    else:
        debug_level = git_config('hooks.debuglevel')
        if not debug_level.isdigit():
            raise InvalidUpdate('Invalid hooks.debuglevel value: %s '
                                '(must be integer >= 0)')
    debug_level = int(debug_level)

    if debug_level >= level:
        warn(msg, prefix='  ' * (level - 1) + 'DEBUG:')


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

