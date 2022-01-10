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

```console
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

```console
$ ./run-validation-tests ZZZZ-999__xfail_check
```
... will run the testcase located in `tests/ZZZZ-999__xfail_check/`.

## Anatomy of a testcase

Each testcase is materialized via a directory in the `testsuite/test`
directory.

The should contain the following:

  - An archive called git-repos.tar.bz2 which, when unpacked,
    contains two Git repositories: One in a directory called `repo`,
    and the other under `bare/repo.git`.

    The typical scenario is that the `bare/repo.git` repository
    represents the shared repository where all users push
    their commits, while the repository in the `repo` directory
    represents the user's clone of the repository in `bare/repo.git`.

    As the name suggests, the repository in `bare/repo.git` should
    normally be a bare repository, as this is how most projects
    are probably set up, but this is not a requirement.

    Note that the reason why those test repositories are packed
    inside an archive is because we cannot commit inside a Git
    repository another Git repository.

  - A Python script called `run_test.py` which implements all
    the testing to be performed by this testcase.

  - Optional: A script implementing the `hooks.style-checker`
    hook. This is for testcases where the style-checker is
    expected to be called.

    Note that the testsuite changes the default value of
    the `hooks.style-checker` configuration to
    `<testcase_dir>/cvs_check.py`. This allows each testcase
    to provide its own version of this hook tailored to
    the needs of the testcase itself.

    Testcases that do not expect to see the style-checker
    being called do not need to provide one.

  - A file named `bare_repo_config` which contains a copy
    of config file in the `bare/repo.git` repository.

    Having this copy makes it easier to perform audits of the bare
    repositories' config, for files which are otherwise buried
    inside a tarball (`git-repos.tar.bz2` tarball described above).

    This file is created automatically if you use the
    `testsuite/bin/pack-test-repos` script.

  - A file named `hooks_config`, which is a copy of the git-hooks'
    configuration in the `bare/repo.git` repository.

    Having this copy makes it easier to perform audits of
    the git-hooks' configuration used by each testcases,
    accessing files which are otherwise buried inside
    a tarball (`git-repos.tar.bz2` tarball described above).

## Testsuite Framework

The testsuite uses pytest as its main engine.

### The `testcase` fixture

Testcases have access to a `testcase` fixture which should
help cover most of the testing needs. See the `TestcaseFixture`
class in `testsuite/conftest.py` for more info about all
services it provides.

### The scripts in `testsuite/bin`

The testsuite also provides a number of little scripts
located in the `testsuite/bin` directory:

  - `pack-test-repos`: This script packs the `bare/repo.git`
    and `repo` repositories into a single archive whose name
    is `git-repos.tar.bz2`. It also creates the `bare_repo_config`
    and `hooks_config` files (see the section describing
    the anatomy of a testcase for more info about those files).

    This script is useful for testcase developers, helping
    automate that conversion of the repositories into tarballs,
    ready for testcase execution.

  - `unpack-test-repos`: This script does the opposite of
    the `pack-test-repos` script.

    It is normally used by the testcase during the setup phase,
    but users might want to use it as well, if they want to access
    and perhaps even change the contents of those repositories.

  - `stdout-logger`: A script simulating the syslog logger
    by providing the same command-line interface as the `logger`
    program. This script prints the message to standard output,
    allowing the testsuite to see and verify all syslog operations.

    The testsuite configures the git-hooks to use this script
    in place of the standard logger.

  - `stdout-sendmail`: A small script mimicking the sendmail
    program by providing the same command-line interface.
    Instead of actually sending emails, it prints their contents
    on standard output, allowing the testsuite to see and verify
    all emails being sent.

  - `stdout-sendmail-wrapper`: A simple wrapper which essentially
    calls `stdout-sendmail`. See the comment inside that script
    for more details behind its existence.

    The testsuite configures the git-hooks to use this script
    in place of the standard sendmail program.

## Managing the Testcases' Repositories

The recommended procedure for creating a set of test repositories
for a testcase is to either start from scratch, or when another
testcase has a set with data which can be reused, to modify
a copy of that other testcase's set of repositories.

To create a repository from scratch, it is recommended to work
as follow:

First, create an empty bare repository, to represent the reference
repository to which users are pushing their change, and thus where
the git-hooks are going to be installed:

```console
$ cd tests/<testcase_dir>
$ mkdir -p bare/repo.git
$ (cd bare/repo.git && git init --bare)
# Make sure to delete the default `hooks` directory, as
# it would get in the way during the testcase execution
# when it tries to install the git-hooks.
$ rm -rf bare/repo.git/hooks
```

Next, create the non-bare repository, and add an "origin" remote
pointing to the repository in `bare/repo.git`:

```console
$ mkdir repo
$ cd repo
$ git init
$ git remote add origin ../bare/repo.git
```

:warning: It is important that the path in the remote's configuration
be a relative path, i.e `../bare/repo.git`, in order to make
the testcase portable. This is why we're creating `repo` with
`git init` followed by `git remote`. If you decide to use `git clone`
instead, be aware that this command transforms the path to the remote
to an absolute path.

From there, you can update both `repo` and `bare/repo.git` as needed
for the testcase.

Once both repositories have been set up to satisfaction, use the
`testsuite/bin/pack-test-repos` script to turn these repositories
into a tarball with the proper name as expected by the testsuite's
infrastructure.

To inspect the repositories, or make modifications, use the
`testsuite/bin/unpack-test-repos` script to unpack them.

:information_source: Note that the `unpack-test-repos`
operation followed by the `pack-test-repos` operation is not
idempotent. If you unpack to inspect the repositories, and
then repack, the resulting `git-repos.tar.bz2` will be different,
even if you made no modification. This is a known limitation of
the testsuite's infrastructure, and there are no plans to lift
this limitation. In that situation, you can (and should!) use
git commands to undo those useless changes.
