from datetime import datetime
from os import environ
import os
import pwd
import re
import sys
from tempfile import mkdtemp

from config import git_config
from errors import InvalidUpdate

############################################################################
#
#  Information related to the environment.
#
############################################################################


def get_user_name():
    """Return the user name (in the Unix sense: The account name).
    """
    if 'GIT_HOOKS_USER_NAME' in environ:
        return environ['GIT_HOOKS_USER_NAME']
    else:
        return pwd.getpwuid(os.getuid()).pw_name


def get_user_full_name():
    """Return the user's full name."""
    if 'GIT_HOOKS_USER_FULL_NAME' in environ:
        full_name = environ['GIT_HOOKS_USER_FULL_NAME']
    else:
        full_name = pwd.getpwuid(os.getuid()).pw_gecos

    # If the fullname contains an email address, or a comma, strip
    # all that.  This would otherwise cause trouble if we used that
    # full_name in an email header.
    m = re.match("([^,<]+)[,<]", full_name)
    if m:
        full_name = m.group(1).strip()

    return full_name


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
    by setting the `GIT_HOOKS_DEBUG_LEVEL' environment variable, or else
    by setting the hooks.debug-level git config value.  The value
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
    if 'GIT_HOOKS_DEBUG_LEVEL' in environ:
        debug_level = environ['GIT_HOOKS_DEBUG_LEVEL']
        if not debug_level.isdigit():
            raise InvalidUpdate('Invalid value for GIT_HOOKS_DEBUG_LEVEL: %s '
                                '(must be integer)' % debug_level)
        debug_level = int(debug_level)
    else:
        debug_level = git_config('hooks.debug-level')

    if debug_level >= level:
        warn(msg, prefix='  ' * (level - 1) + 'DEBUG: ')


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
            Default value is '*** '.
    """
    prefix = kwargs['prefix'] if 'prefix' in kwargs else '*** '
    for arg in args:
        print >> sys.stderr, "%s%s" % (prefix, arg)


############################################################################
#
# Misc...
#
############################################################################

def indent(text, indentation):
    """Indent every line with indentation.

    PARAMETERS
        text: A string.
        indentiation: A string used to indent every non-empty line.

    RETURN VALUE
        The indented version of text.
    """
    indented = []
    for line in text.splitlines(True):
        indented.append(indentation + line)
    return ''.join(indented)


def ref_matches_regexp(ref_name, ref_re):
    """Return true iff a reference's name matches the given pattern.

    PARAMETERS
        ref_name: The name of the reference we want to match against ref_re.
        ref_re: A regular expression.

    RETURN VALUE
        True if ref_name matches ref_re. False otherwise.
    """
    m = re.match(ref_re, ref_name)
    if m is None:
        return False
    # We also need to verify that the namespace pattern matches
    # the whole reference name (i.e. we do not want a reference
    # named 'refs/heads/master2' be considered part of a namespace
    # whose regexp is 'refs/heads/master').
    #
    # With Python 2.7, the simplest is to just verify the extent
    # of the string being matched. Once we transition to Python 3,
    # we can simplify this by using re.fullmatch instead of re.match.
    return m.end() - m.start() == len(ref_name)


class FileLock(object):
    """An object implementing file locking (work in "with" statement only).

    The locking is relying on os.link being atomic, and thus only
    works on Unix systems.
    """
    def __init__(self, filename):
        """The constructor.

        PARAMETERS
            filename: The name of the file to be locking.  If the file
                does not exist at the time this class is instantiated,
                it is automatically created.
        """
        self.filename = filename
        self.lock_filename = self.filename + '.lock'
        # Make sure the file to be locked exists; if not, create it now.
        if not os.path.exists(self.filename):
            # Use mode 'a' instead of 'w' to avoid truncating the file
            # if someone opens the same file at the same time.
            open(self.filename, 'a').close()
            os.chmod(self.filename, 0664)

    def __enter__(self):
        try:
            os.link(self.filename, self.lock_filename)
            # Just in case the lock is accidently left behind, write
            # some information that helps us track the author of
            # the lock.
            with open(self.lock_filename, 'w') as f:
                f.write('locked by user %s at %s (pid = %d)\n'
                        % (get_user_name(), str(datetime.now()), os.getpid()))
        except Exception:
            # It would be better if the warning was part of the InvalidUpdate
            # exception date, since a client handling the lock failure
            # might have prefered to silence the warning???  But that would
            # require us to add a keyword argument to handle error message
            # prefixes. Good enough for now.
            warn('-' * 69,
                 '--  Another user is currently pushing changes to this'
                 ' repository.  --',
                 '--  Please try again in another minute or two.       '
                 '              --',
                 '-' * 69,
                 prefix='')
            raise InvalidUpdate

    def __exit__(self, type, value, traceback):
        os.unlink(self.lock_filename)
