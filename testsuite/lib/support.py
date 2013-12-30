import gnatpython.ex
from gnatpython.fileutils import diff

import os
import sys
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
        os.environ['GIT_HOOKS_STYLE_CHECKER'] = '%s/cvs_check.py' % os.getcwd()

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

    def git_version(self):
        """Return the git version number (a LooseVersion object).
        """
        from distutils.version import LooseVersion
        p = gnatpython.ex.Run(['git', '--version'])
        assert (p.status == 0)
        out = p.out.splitlines()
        assert (len (out) > 0)
        assert (out[0].startswith('git version '))
        version_str = out[0].replace('git version ', '')
        return LooseVersion(version_str)

    def assertRunOutputEqual(self, r, expected_out):
        """assert that r.cmd_out is equal to expected_out...

        ... And if the assertion is not met, then produce a useful
        output.
        """
        self.assertEqual(expected_out, r.cmd_out, r.diff(expected_out))


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

        # git version 1.7.8.2 prints the non-fast-forward error
        # message differently from 1.7.10.4...  The message is
        # at the end, so check there...
        NON_FAST_FORWARD_ERROR_1_7_8_2 = """\
To prevent you from losing history, non-fast-forward updates were rejected
Merge the remote changes (e.g. 'git pull') before pushing again.  See the
'Note about fast-forwards' section of 'git push --help' for details."""
        NON_FAST_FORWARD_ERROR_1_7_10_4 = """\
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. Merge the remote changes (e.g. 'git pull')
hint: before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details."""
        if lines[-3:] == NON_FAST_FORWARD_ERROR_1_7_8_2.splitlines():
            lines[-3:] = NON_FAST_FORWARD_ERROR_1_7_10_4.splitlines()

        result = []
        for line in lines:
            # Remove any clear-end-of-line terminal control sequences...
            line = line.replace('\033[K', '')

            # git version 1.6.5.rc2 spells 'non-fast forward', whereas
            # git version 1.7.1 spells 'non-fast-forward'. Unify on
            # the latest spelling...
            line = line.replace('non-fast forward', 'non-fast-forward')

            # git version 1.7.8.2 still spells '1 files changed',
            # instead of '1 file changed' (in 1.7.10.4).
            line = line.replace('remote:  1 files changed,',
                                'remote:  1 file changed,')

            # Same as above for insertions and deletions...
            line = line.replace(', 1 insertions(+)', ', 1 insertion(+)')
            line = line.replace(', 1 deletions(-)', ', 1 deletion(-)')

            # Same, but with "0 insertions" and "0 deletions", which
            # is printed by git version 1.7.8.2, but not by newer
            # versions (1.7.10.4).
            line = line.replace(', 0 insertions(+)', '')
            line = line.replace(', 0 deletions(-)', '')

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

    def diff(self, expected_out):
        """Return self.out followed by a diff self.cmd_out and expected_out.

        PARAMETERS
            expected_out: A string containing the expected output.
        """
        diff_str = diff(expected_out.splitlines(),
                        self.cmd_out.splitlines())
        return '%s\n\nDiff:\n\n%s' % (self.image, diff_str)
