from gnatpython.fileutils import mkdir, cd
from gnatpython.internal.excross import PIPE, run_cross

import os
import sys
import re
import unittest

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

    def enable_unit_test(self):
        """Setup the environment in a way that allows us to perform unit test.
        """
        sys.path.insert(0, '%s/bare/repo.git/hooks' % TEST_DIR)


def runtests():
    """Call unittest.main.
    """
    unittest.main()


def ex_run_image(p):
    """Return a diagnostic image of the given gnatpython.ex.Run object.

    PARAMETERS
        p: A gnatpython.ex.Run object.

    LIMITATIONS
        This function assumes that the process has run until completion.
    """
    return '%% %s -> %s\n%s' % (p.command_line_image(), p.status, p.out)

######################################################################
#
#  Some often-used symbols we re-export here, to help writing testcases...
#
######################################################################

from gnatpython.fileutils import *
from gnatpython.ex import Run
