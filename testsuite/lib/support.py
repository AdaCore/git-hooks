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
