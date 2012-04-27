"""A module providing some generally useful stuff.
"""

import sys

def abort(exit_code=0):
    """Abort the execution of the current process.  Any cleanup that
    might be needed before aborting is guaranteed to be performed.

    PARAMETERS
       exit_code: The process exit code sent to the parent process.

    REMARKS
       This function is meant to be a routine that knows what to do
       depending on whether we're inside the main-loop process, or
       if we're inside a testcase process.  As of the time of this writing,
       it is sufficient for either process to just call sys.exit.  But
       there might come a day when we might need to do different things
       depending on the process.
    """
    sys.exit(exit_code)

def fatal_error(msg):
    """Print the given message on standard output and then exit immediately.

    PARAMETERS
      msg: The error message to print.
    """
    print "*** Error: " + msg
    abort(1)


