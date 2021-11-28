import distutils.dir_util
from e3.diff import diff
import e3.os.process
import os
import pytest
import shutil
import sys
import tempfile


@pytest.fixture(autouse=True, scope="function")
def env_setup(request):
    # Save our current working environment.
    saved_cwd = os.getcwd()
    saved_environ = os.environ.copy()

    # Create a temporary directory inside which we will be working from.
    tmp_dir = tempfile.mkdtemp("", "git-hooks-")

    # Create a directory inside our tmp_dir that we'll use for running
    # our testcase.
    work_dir = os.path.join(tmp_dir, "src")
    os.mkdir(work_dir)
    os.chdir(work_dir)

    # Create a directory inside our tmp_dir that we'll tell the tempfile
    # module to use by default (via the appropriate environment variable).
    # The goal is to verify that the git-hooks do not leak any temporary
    # file or directory it might be creating, by verifying at the end
    # of the test that this temporary directory is empty.
    git_hooks_tmp_dir = tempfile.mkdtemp("", "git-hooks-")
    git_hooks_tmp_dir = os.path.join(tmp_dir, "tmp")
    os.mkdir(git_hooks_tmp_dir)
    for var_name in ("TMPDIR", "TEMP", "TMP"):
        os.environ[var_name] = git_hooks_tmp_dir

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
    os.environ["GIT_HOOKS_STYLE_CHECKER"] = f"{work_dir}/cvs_check.py"

    # Unset various environment variables that the hooks respond to.
    # We do not want the user environment to influence the hooks' behavior
    # during testing.
    for var_name in ("GIT_HOOKS_CVS_CHECK", "GIT_HOOKS_DEBUG_LEVEL"):
        if var_name in os.environ:
            del os.environ[var_name]

    def env_teardown():
        os.environ.clear()
        os.environ.update(saved_environ)

        git_hooks_tmp_dir_contents = os.listdir(git_hooks_tmp_dir)
        assert not git_hooks_tmp_dir_contents, git_hooks_tmp_dir_contents

        os.chdir(saved_cwd)
        shutil.rmtree(tmp_dir)

    request.addfinalizer(env_teardown)


class TestcaseFixture:
    """A class to be used as a testcase fixture.

    :ivar root_dir: This git-hooks repository's root directory.
    :ivar testsuite_dir: The root of the testsuite directory.
    :ivar testsuite_bin_dir: The testsuite's "bin" directory (where various
        programs used by the testsuite are located).
    :ivar src_dir: The directory where the sources of the testcase are located.
        These are the original sources located within the repository itself,
        so the testcase should never modify its contents. The sources are
        copied into self.work_dir, so use this area and attribute instead.
    :ivar work_dir: A temporary location where the testcase has been set up.
        This includes copying the contents of the src_dir, as well as various
        other operations designed to make the testcase ready for execution
        (e.g. unpacking of the test repo included in the testcase).
    :ivar repo_dir: The path to the non-bare repository to be used by our testcase.
    :ivar bare_repo_dir: The path to the bare repository to be used by our testcase.
    :ivar git_output_massager: A GitOutputMassager object.
    """

    def __init__(self, root_dir, testcase_src_dir, testcase_work_dir):
        """Initialize a TestcaseFixture object.

        :param root_dir: Same as the attribute.
        :param testcase_src_dir: Same as the attribute.
        :param testcase_work_dir: Same as the attribute.
        """
        self.root_dir = root_dir
        self.testsuite_dir = os.path.join(self.root_dir, "testsuite")
        self.testsuite_bin_dir = os.path.join(self.testsuite_dir, "bin")
        self.src_dir = testcase_src_dir
        self.work_dir = testcase_work_dir
        self.repo_dir = os.path.join(self.work_dir, "repo")
        self.bare_repo_dir = os.path.join(self.work_dir, "bare", "repo.git")
        self.git_output_massager = GitOutputMassager(self.git_version())

        # Set the testcase up, by copying everything from the testcase's
        # source directory, into the current directory.
        distutils.dir_util.copy_tree(self.src_dir, self.work_dir)

        # Next, unpack the git repositories used by this testcase.
        self.safe_run(
            [os.path.join(self.testsuite_bin_dir, "unpack-test-repos")],
            cwd=self.work_dir,
        )

        # And finally, "install" a copy of the git hooks in the bare
        # repository.  Avoid a copy, and simply create a link, which
        # is actually what we do in practice for our real repositories.
        if os.path.isdir(os.path.join(self.bare_repo_dir, ".git")):
            # This is a non-bare repository (a bit unusual, but
            # supported as well).  In that case, the git dir is
            # that .git/ subdirectory.
            self.bare_repo_dir = os.path.join(self.bare_repo_dir, ".git")
        os.symlink(
            os.path.join(self.root_dir, "hooks"),
            os.path.join(self.bare_repo_dir, "hooks"),
        )

        # Also, tell the hooks to use our fake (syslog) logger,
        # rather than the real logger.
        os.environ["GIT_HOOKS_LOGGER"] = os.path.join(
            self.root_dir, "testsuite", "bin", "stdout-logger"
        )

        # Similarly, tell the hooks to use our fake sendmail script,
        # rather than the real one (we want those emails to be dumped
        # on stdout, rather than actually sent out).
        os.environ["GIT_HOOKS_SENDMAIL"] = os.path.join(
            self.root_dir, "testsuite", "bin", "stdout-sendmail"
        )

    @property
    def hooks_src_dir(self):
        """Return the directory where the git-hooks sources are located."""
        # The sources for the git-hooks can be found in the "<root>/hooks"
        # directory, where "<root>" is the root of this repository.
        return os.path.join(self.root_dir, "hooks")

    def run(self, cmds, input=None, cwd=None, env=None, ignore_environ=False):
        """Run the given command(s).

        This is a simple-minded wrapper around the Run class, provided here
        to standardize a bit calls to external programs made through the Run
        class. This wrapper behaves identically to the Run class, with the
        exception of the following difference:

            - If "cwd" is None, then we use self.repo_dir as the directory
              to run the program from, rather than the actual working directory.

              This is because the majority of commands we want to run during
              testing are git commands to be run from the non-bare repository.
              Use that non-bare repository directory as the default allows us
              to simplify the code of our testcases.

            <no other difference for now>
        """
        if cwd is None:
            cwd = self.repo_dir
        return Run(cmds, input=input, cwd=cwd, env=env, ignore_environ=ignore_environ)

    def safe_run(self, cmds, cwd=None):
        """Call self.run, and raise an assertion if the command returned nonzero."""
        r = self.run(cmds, cwd=cwd)
        self.assertEqual(r.status, 0, r.image)

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

        The purpose of running the unit testing as a subprocess
        is to protect the testcase from any change in environment
        done as part of performing the unit testing.

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
            cwd = os.path.join(self.work_dir, "bare", "repo.git")

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

        p = e3.os.process.Run(["git", "--version"])
        assert p.status == 0
        out = p.out.splitlines()
        assert len(out) > 0
        assert out[0].startswith("git version ")
        version_str = out[0].replace("git version ", "")
        return LooseVersion(version_str)

    def massage_git_output(self, git_output):
        """Massage git_output as explained in class GitOutputMassager's documentation.

        :param git_output: Same as GitOutputMassager.massage.
        """
        return self.git_output_massager.massage(git_output)

    def assertEqual(self, lhs, rhs, msg_if_fails):
        """Verify that lhs is equal to rhs or else raise a failed assertion.

        PARAMETERS
            lhs: The first value to check for equality.
            rhs: The other value to check for equality.
            msg_if_fails: A message to print if the assertion fails.
        """
        assert lhs == rhs, msg_if_fails

    def assertNotEqual(self, lhs, rhs, msg_if_fails):
        """Verify that lhs is not equal to rhs or raise a failed assertion.

        PARAMETERS
            lhs: The first value to check for inequality.
            rhs: The other value to check for inequality.
            msg_if_fails: A message to print if the assertion fails.
        """
        assert lhs != rhs, msg_if_fails

    def assertRunOutputEqual(self, r, expected_out):
        """assert that r.cmd_out is equal to expected_out...

        ... And if the assertion is not met, then produce a useful
        output.
        """
        self.assertEqual(r.cmd_out, expected_out, r.diff(expected_out))


@pytest.fixture(scope="function")
def testcase(pytestconfig, request):
    """Return a TestcaseFixture object."""
    testcase_script_filename = request.fspath.strpath
    testcase_src_dir = os.path.dirname(testcase_script_filename)
    return TestcaseFixture(
        root_dir=pytestconfig.rootdir.strpath,
        testcase_src_dir=testcase_src_dir,
        testcase_work_dir=os.getcwd(),
    )


class Run(e3.os.process.Run):
    """An e3.os.process.Run subclass providing access to a sanitized output."""

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


class GitOutputMassager:
    """A class to centralize the management of Git output across Git versions.

    The purpose of this class is to automate the transformation of the output
    we expect from the latest Git commands into the output that was produced
    in earlier versions of Git. This allows us to run the testsuite, where
    the check for test success is based on strict output comparison and is
    therefore not flexible at all, with multiple versions of Git.

    :ivar git_version: A LooseVersion object of the version of Git.
    """

    def __init__(self, git_version):
        """Initialize self.

        :param git_version: Same as the attribute.
        """
        self.git_version = git_version

    def massage(self, git_output):
        """Massage the given git_output as explained in the class's documentation.

        :param git_output: The git command's output we want to adjust (an str).
        """
        result = git_output

        if self.git_version < "2.29":
            # When pushing new references which are not branches (such as
            # refs/notes/commits, more recent versions of Git now print...
            #
            #    * [new reference]   xxx -> <ref_name>
            #
            # ... whereas, with older versions, we expect...
            #
            #    * [new branch]      xxx -> <ref_name>
            result = result.replace(" * [new reference]", " * [new branch]   ")

        return result
