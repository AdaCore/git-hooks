import gnatpython.ex
from gnatpython.fileutils import diff

import os
import sys
from tempfile import mkdtemp
import unittest


class TestCase(unittest.TestCase):
    @property
    def hooks_src_dir(self):
        """Return the directory where the git-hooks sources are located."""
        # The sources for the git-hooks ca be found in the "hooks"
        # directory, two directory levels up from this unit.
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "hooks",
            )
        )

    @property
    def work_dir(self):
        return os.path.abspath(os.path.dirname(sys.modules["__main__"].__file__))

    @property
    def repo_dir(self):
        """Return the path to the testcase's non-bare repository."""
        return os.path.join(self.work_dir, "repo")

    @property
    def bare_repo_dir(self):
        """Return the path the testcase's bare repository."""
        return os.path.join(self.work_dir, "bare", "repo.git")

    def setUp(self):
        # Override the global git user name, to help making sure
        # the output does not depend on who is running the testsuite.
        os.environ["GIT_AUTHOR_EMAIL"] = "hooks-tester@example.com"
        os.environ["GIT_AUTHOR_NAME"] = "hooks tester"

        # Export GIT_HOOKS_TESTSUITE_MODE so that the hooks know
        # that we are in testsuite mode, thus replacing certain
        # features, such as email, by simple traces.
        os.environ["GIT_HOOKS_TESTSUITE_MODE"] = "true"

        # Other "parameters" that should normally be taken from the
        # environment, but which we want to override here.  Pretend
        # that the hooks are calld by user "Test Suite".
        os.environ["GIT_HOOKS_USER_NAME"] = "testsuite"
        os.environ["GIT_HOOKS_USER_FULL_NAME"] = "Test Suite"

        # Tell the hooks to use a "fake" cvs_check script. Each
        # testcase will want to have their own, because each testcase
        # have different requirements regarding how it should behave
        # for the purpose of the testcase.
        #
        # By default, the testcase's cvs_check script is called
        # cvs_check.py and is located at the root of the testcase
        # directory.
        os.environ["GIT_HOOKS_STYLE_CHECKER"] = "%s/cvs_check.py" % self.work_dir

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
        self.testcase_tmp_dir = mkdtemp("", "", os.environ["GIT_HOOKS_TESTSUITE_TMP"])
        os.environ["TMP"] = self.testcase_tmp_dir
        os.environ["TMPDIR"] = self.testcase_tmp_dir

        # Allow users to call self.run as if they were calling self._run,
        # which is a wrapper around Run.
        #
        # The reason why do it this way rather than simply define
        # the "run" method as usual, is because unittest.TestCase
        # actuall does provide one already, and uses that method to
        # run the testcase. It means our choice to use "self.run"
        # is conflicting with the unittest.TestCase framework.
        # This is only temporary, however, as we're working on
        # transitioning this testcase to pytest instead, at which
        # point this will no longer be an issue.
        self.run = self._run

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
        os.environ["GIT_HOOKS_DEBUG_LEVEL"] = str(level)

    def change_email_sending_verbosity(self, full_verbosity):
        """Change the verbosity level of email sending.

        PARAMETERS
            full_verbosity: If True (the default unless this method
                is called), the email traces printed by the git-hooks
                provide a full dump of the email, allowing complete
                verification of its contents. If False, the traces
                are kept very compact, allowing the verification that
                emails are being sent, but no more. The latter is useful
                for testcase where the contents of the emails is not
                important.
        """
        verbosity_varname = "GIT_HOOKS_MINIMAL_EMAIL_DEBUG_TRACE"
        if full_verbosity:
            if verbosity_varname in os.environ:
                del os.environ[verbosity_varname]
        else:
            os.environ["GIT_HOOKS_MINIMAL_EMAIL_DEBUG_TRACE"] = "set"

    def _run(self, cmds, input=None, cwd=None, env=None, ignore_environ=False):
        """A convenience wrapper to run a program.

        PARAMETERS
            cmds: Same as Run.
            input: Same as Run.
            cwd: The directory from which to run the command, or
                self.repo_dir if None.
            env: Same as Run.
            ignore_environ: Same as Run.
        """
        if cwd is None:
            cwd = self.repo_dir
        return Run(cmds, input=input, cwd=cwd, env=env, ignore_environ=ignore_environ)

    def run_unit_test_script(
        self,
        expected_out,
        cwd=None,
        env=None,
        ignore_environ=False,
    ):
        """Run the script unit_test_script.py in unit test mode.

        This method runs the script "unit_test_script.py" (located in
        the same directory as the run_test.py" script), with its
        environment set such that the script is able to import
        code directly from the git-hooks sources. This is useful
        when trying to test certain parts of the git-hooks code
        which is too difficult or even impossible to reach with
        our standard testing techniques.

        The purpose of this is to allow protect the testcase from
        any change in environment necessary as part of performing
        the unit testing.

        PARAMETERS
            expected_out: The unit test script's expected output.
            cwd: The directory from which the script should be
                executed. If None, we executed the script from
                the root of the testcase's bare repository.
            env: Same as self.run.
            ignore_environ: Same as self.run.
        """
        # The git-hooks infrastructure assume that the current working
        # directory when being called is the root of the git repository.
        # So unless cwd was explicitly specified, assume we always want
        # to perform the unit test using that directory.
        if cwd is None:
            cwd = self.bare_repo_dir

        # Create a copy of the environment we want to pass to the unit test
        # script, and then modify it to set unit-testing up.
        augmented_env = {}
        if not ignore_environ:
            augmented_env = os.environ.copy()
        if env is not None:
            augmented_env.update(env)

        # Set PYTHONPATH up to include the path to the git-hooks sources.
        augmented_env["PYTHONPATH"] = ":".join(
            [self.hooks_src_dir, augmented_env.get("PYTHONPATH", "")]
        )

        augmented_env["PYTHONUNBUFFERED"] = "yes"

        p = self.run(
            [
                sys.executable,
                # Force the stdout and stderr streams to be unbuffered.
                # That way, if the unit test script writes to both stdout
                # and stderr, the output will be in the correct order.
                "-u",
                os.path.join(self.work_dir, "unit_test_script.py"),
            ],
            cwd=cwd,
            env=augmented_env,
            ignore_environ=ignore_environ,
        )
        assert p.status == 0, p.image
        self.assertRunOutputEqual(p, expected_out)

    def git_version(self):
        """Return the git version number (a LooseVersion object)."""
        from distutils.version import LooseVersion

        p = gnatpython.ex.Run(["git", "--version"])
        assert p.status == 0
        out = p.out.splitlines()
        assert len(out) > 0
        assert out[0].startswith("git version ")
        version_str = out[0].replace("git version ", "")
        return LooseVersion(version_str)

    def assertRunOutputEqual(self, r, expected_out):
        """assert that r.cmd_out is equal to expected_out...

        ... And if the assertion is not met, then produce a useful
        output.
        """
        self.assertEqual(expected_out, r.cmd_out, r.diff(expected_out))


def runtests():
    """Call unittest.main."""
    unittest.main()


class Run(gnatpython.ex.Run):
    """A gnatpython.ex.Run subclass providing access to a sanitized output."""

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
            line = line.replace("\033[K", "")

            # git version 1.6.5.rc2 spells 'non-fast forward', whereas
            # git version 1.7.1 spells 'non-fast-forward'. Unify on
            # the latest spelling...
            line = line.replace("non-fast forward", "non-fast-forward")

            # git version 1.7.8.2 still spells '1 files changed',
            # instead of '1 file changed' (in 1.7.10.4).
            line = line.replace("remote:  1 files changed,", "remote:  1 file changed,")

            # Same as above for insertions and deletions...
            line = line.replace(", 1 insertions(+)", ", 1 insertion(+)")
            line = line.replace(", 1 deletions(-)", ", 1 deletion(-)")

            # Same, but with "0 insertions" and "0 deletions", which
            # is printed by git version 1.7.8.2, but not by newer
            # versions (1.7.10.4).
            line = line.replace(", 0 insertions(+)", "")
            line = line.replace(", 0 deletions(-)", "")

            # Lastly, strip any trailing spaces.  We strip them because
            # we do not want to be a the mercy of git's trailing spaces
            # when matching the output of commands, and because they are
            # not very important visually for the user.   On the other
            # hand, we do not want to strip leading spaces, at least
            # for now, as they do affect the output seen by the user.
            line = line.rstrip()
            result.append(line)
        return "\n".join(result) + "\n"

    @property
    def image(self):
        """Return an image of the command and its result and output.

        REMARKS
            This assumes that this command has run to completion.
        """
        return "%% %s -> %s\n%s" % (
            self.command_line_image(),
            self.status,
            self.cmd_out,
        )

    def diff(self, expected_out):
        """Return self.out followed by a diff self.cmd_out and expected_out.

        PARAMETERS
            expected_out: A string containing the expected output.
        """
        diff_str = diff(
            expected_out.splitlines(),
            self.cmd_out.splitlines(),
            ignore_white_chars=False,
        )
        return "%s\n\nDiff:\n\n%s" % (self.image, diff_str)
