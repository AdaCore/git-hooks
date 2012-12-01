from gnatpython.env import Env
import gnatpython.ex
from gnatpython.fileutils import mkdir, cd
from gnatpython.internal.excross import PIPE, run_cross

import os
import sys
import re
from tempfile import mkdtemp
import unittest

# The imports below are not necessarily used by this module.
# They are just being re-exported here for the benefit of
# the testcases, as they tend to be used often.
from gnatpython.fileutils import *

TEST_DIR = os.path.dirname(sys.modules['__main__'].__file__)
TEST_DIR = os.path.abspath(TEST_DIR)

class TestCase(unittest.TestCase):
    def setUp(self):
        # Export GIT_HOOKS_TESTSUITE_MODE so that the hooks know
        # that we are in testsuite mode, thus replacing certain
        # features, such as email, by simple traces.
        os.environ['GIT_HOOKS_TESTSUITE_MODE'] = 'true'

        # Other "parameters" that should normally be taken from the
        # environment, but which we want to override here.  Pretend
        # that the hooks are calld by user "Test Suite".
        os.environ['GIT_HOOKS_USER_NAME'] = 'testsuite'
        os.environ['GIT_HOOKS_USER_FULL_NAME'] = 'Test Suite'

        # Tell the hooks to use a "fake" cvs_check script. Each
        # testcase will want to have their own, because each testcase
        # have different requirements regarding how it should behave
        # for the purpose of the testcase.
        #
        # By default, the testcase's cvs_check script is called
        # cvs_check.py and is located at the root of the testcase
        # directory.
        os.environ['GIT_HOOKS_CVS_CHECK'] = '%s/cvs_check.py' % os.getcwd()

        # Create a directory to be used as tmp by this testcase.
        # We want that directory to be inside the testsuite's
        # global tmp directory, so that anything accidently left
        # behind will be automatically caught and cleaned up by
        # the mainloop.
        #
        # The objective is to force the scripts to use this testcase
        # tmp directory during testing, allowing us to verify once
        # the testcase returns that the git-hooks scripts do not leak
        # any temporary files/directories. We do this by force-setting
        # the various environment variables that gnatpython's Env
        # and the tempfile modules use as the default tmp.
        self.testcase_tmp_dir = \
            mkdtemp('', '', os.environ['GIT_HOOKS_TESTSUITE_TMP'])
        os.environ['TMP'] = self.testcase_tmp_dir
        os.environ['TMPDIR'] = self.testcase_tmp_dir

    def tearDown(self):
        # One last check: Verify that the scripts did not leak any
        # temporary files/directories, by looking at the number of
        # files in the testcase tmp dir (we forced all scripts to
        # use this tmp directory during the setUp phase).
        self.assertFalse(os.listdir(self.testcase_tmp_dir))

    def set_debug_level(self, level):
        """Set the debug level to the given value.

        This is a convenience function that allows testcases to
        set the debug level without having to know how the git
        hooks infrastructure implements it.

        PARAMETERS
            level: Typically, a natural integer.  But it can be any
                value - this function automatically turns it into
                a string and uses it as the debug level.  This allows
                us to set the debug level to an invalid value as well.
        """
        os.environ['GIT_HOOKS_DEBUG_LEVEL'] = str(level)

    def enable_unit_test(self):
        """Setup the environment in a way that allows us to perform unit test.
        """
        sys.path.insert(0, '%s/bare/repo.git/hooks' % TEST_DIR)
        # Also, we need to cd to the bare repository, as the hooks
        # assumes we are being called from there.
        os.chdir('%s/bare/repo.git' % TEST_DIR)


def runtests():
    """Call unittest.main.
    """
    unittest.main()


class Run(gnatpython.ex.Run):
    """A gnatpython.ex.Run subclass providing access to a sanitized output.
    """
    @property
    def cmd_out(self):
        """Same as self.out, except that the output is sanitized.

        RETURN VALUE
            A sanitized version of self.out.  For instance, it strips
            certain terminal control characters out of it before
            returning it.
        """
        lines = self.out.splitlines()
        result = []
        for line in lines:
            # Remove any clear-end-of-line terminal control sequences...
            line = line.replace('\033[K', '')
            # git version 1.6.5.rc2 spells 'non-fast forward', whereas
            # git version 1.7.1 spells 'non-fast-forward'. Unify on
            # the latest spelling...
            line = line.replace('non-fast forward', 'non-fast-forward')
            # Lastly, strip any trailing spaces.  We strip them because
            # we do not want to be a the mercy of git's trailing spaces
            # when matching the output of commands, and because they are
            # not very important visually for the user.   On the other
            # hand, we do not want to strip leading spaces, at least
            # for now, as they do affect the output seen by the user.
            line = line.rstrip()
            result.append(line)
        return '\n'.join(result) + '\n'

    @property
    def image(self):
        """Return an image of the command and its result and output.

        REMARKS
            This assumes that this command has run to completion.
        """
        return '%% %s -> %s\n%s' % (self.command_line_image(),
                                    self.status,
                                    self.cmd_out)
