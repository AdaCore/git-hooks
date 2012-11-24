from gnatpython.env import Env
from gnatpython.fileutils import mkdir, cd
from gnatpython.internal.excross import PIPE, run_cross

import os
import sys
import re
from tempfile import mkdtemp
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
