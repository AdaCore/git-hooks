#!/usr/bin/env python
"""./testsuite.py [OPTIONS] [tests_name(s)]

Driver for the git hooks testsuite.
"""

from gnatpython.env import Env
from gnatpython.fileutils import rm
from gnatpython.main import Main
from gnatpython.mainloop import (MainLoop, add_mainloop_options,
                                 generate_collect_result,
                                 generate_run_testcase,
                                 setup_result_dir)
from gnatpython.testdriver import add_run_test_options
import os

from tempfile import mkdtemp
from utils import fatal_error

# The name of the script to execute in order to run a testcase.
TESTCASE_SCRIPT_NAME = 'test.py'

# When the user does not specify specific testcases on the command
# line, then assume that we should be running the entire testsuite,
# which is located in the following directory.
DEFAULT_TESTCASE_DIR = "tests"


def get_testcases(testcase_dirs):
    """Return the list of testcases to run, by recursively inspecting
    the contents of the directories provided in the testcase_dirs list.

    The returned list is sorted in alphabetical order, so as to make
    two runs of the same testcases for the same platform comparable.

    PARAMETERS
        testcase_dirs: A list of directory names inside which the testsuite
            should look for testcases to run.  If empty, then default to
            DEFAULT_TESTCASE_DIR if that directory exists.

    RETURN VALUE
        A list of testcases to run.
    """
    # Note: We use a dictionary to store the list of testcase as
    # we are building it as a way of eliminating duplicates...
    testcases = {}
    # If no testcase was specified on the command line, then try
    # the default testcase directory.
    if not testcase_dirs:
        if not os.path.isdir(DEFAULT_TESTCASE_DIR):
            fatal_error("No testcase specified")
        testcase_dirs = [DEFAULT_TESTCASE_DIR]
    for testcase_dir in testcase_dirs:
        if not os.path.isdir(testcase_dir):
            fatal_error("Invalid directory name: %s" % testcase_dir)
        for root, dirs, files in os.walk(testcase_dir):
            if TESTCASE_SCRIPT_NAME in files:
                testcases[os.path.realpath(root)] = None
    # One last sanity check: Make sure that we have at least one testcase.
    if not testcases:
        fatal_error("No valid testcase found. Aborting.")
    result = testcases.keys()
    result.sort()
    return result


def print_testsuite_results_summary(metrics):
    """Print a quick summary of the results after a testsuite run.

    ARGUMENTS
        metrics: Same as in gnatpython.mainloop.generate_collect_result.
    """
    print """\

Testsuite Results Summary -- Out of %(run)d testscase(s) run in total:

    %(failed)4d testcase(s) failed
    %(crashed)4d testcase(s) crashed
""" % metrics


def main():
    """Run the testsuite.
    """
    m = Main()
    add_mainloop_options(m, extended_options=True)
    add_run_test_options(m)
    m.add_option("--diffs", dest="view_diffs", action="store_true",
                 default=False, help="show diffs on stdout")
    m.parse_args()

    # Create a tmp directory for the entire testsuite, to make sure
    # that, should the git hooks leak any file/directories, we can
    # (1) detect them, and (2) delete them.
    #
    # This requires some extra work to make sure that the scripts
    # being tested do actually use them, but this needs to be done
    # by each testcase, because we want each testcase to have its
    # own tmp directory (allowing for concurrency).  We pass that
    # information to the testcase through the GIT_HOOKS_TESTSUITE_TMP
    # environment variable.
    m.options.tmp = mkdtemp('', 'git-hooks-TS-', m.options.tmp)
    os.environ['GIT_HOOKS_TESTSUITE_TMP'] = m.options.tmp

    try:
        testcases = get_testcases(m.args)
        setup_result_dir(m.options)

        # We do not need discriminants in this testsuite at the moment.
        discs = None

        metrics = {}
        collect_result = generate_collect_result(metrics=metrics,
                                                 options=m.options)
        run_testcase = generate_run_testcase('bin/run-testcase',
                                             discs, m.options)

        MainLoop(testcases, run_testcase, collect_result,
                 m.options.mainloop_jobs)
        print_testsuite_results_summary(metrics)
    finally:
        rm(m.options.tmp, recursive=True)


if __name__ == '__main__':
    main()
