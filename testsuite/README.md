# AdaCore Git Hooks' Testsuite

This directory contains the Testsuite for the AdaCore Git Hooks,
and this document provides a short introduction to this testsuite.

## Pre-requisites

### Python and Python Packages

This testsuite requires Python version 3.8 or later.

The testsuite is aware of the packages it depends on, and will
double-check they are all available before starting the testing
in earnest. If not, the list of missing Python packages will be
printed and the testsuite will then abort. All dependencies
should be installable via pip.

### Git

The recommended version for running this testsuite is Git version 2.32.x.

Note that the testsuite framework is a bit rigid when it comes to
verifying that a test was succesful, as the default approach is based
on performing a string equality test between the output produced by
Git, and the output we expected from it. As a result, the testsuite
is not well equipped to handle changes in output from Git version to
Git version. This is why running the testsuite with a version other
than the recommended one might produce spurious failures. It's still
possible to support multiple versions, however (see
the `GitOutputMassager` class in `conftest.py`).

## Running the Testsuite

To run the testsuite, simply run the following script:

```
    $ ./run-validation-tests
```

By default, validation will include a style-checking phase followed
by, if no style issues are detected, by a run of the testsuite, and
finish with a code coverage report at the end.

You can disable each of the various elements of the validation via
command-line switches. See the output of the script's `--help`
command-line option for more details on how to do this.

You can also request that a single testcase be run by simply passing
its name as an argument on the command line (the name of a testcase
is the name of the directory containing the testcase). For instance...

```
    $ ./run-validation-tests ZZZZ-999__xfail_check
```
... will run the testcase located in `tests/ZZZZ-999__xfail_check/`.
