import os
from os.path import basename
from pipes import quote
import subprocess
from subprocess import check_output, STDOUT

from git import git, get_module_name, CalledProcessError
from git_attrs import git_attribute
import utils
from utils import InvalidUpdate, debug, warn

def check_file(filename, sha1, commit_rev):
    """Check a file for style violations if appropriate.

    Raise InvalidUpdate if one or more style violations are detected.

    PARAMETERS
        filename: The name of the file to check.
        sha1: The sha1 of the file to be checked.
        commit_rev: The associated commit sha1.  This piece of information
            helps us find the correct version of the .gitattributes files,
            in order to determine whether pre-commit-checks should be
            applied or not.
    """
    debug("check_file (filename=`%s', sha1=%s)" % (filename, sha1), level=3)

    # Determine whether this file has the no-precommit-check attribute
    # set, in which case style-checks should not be performed.
    if git_attribute(commit_rev, filename, 'no-precommit-check') == 'set':
        debug('no-precommit-check: %s commit_rev=%s'
              % (filename, commit_rev))
        return

    # Get a copy of the file and save it in our scratch dir.
    tmp_filename = "%s/%s" % (utils.scratch_dir, os.path.basename(filename))
    git.show(sha1, _outfile=tmp_filename)

    # Call cvs_check.

    # For testing purposes, provide a back-door allowing the user
    # to override the precommit-check program to be used.  That way,
    # the testsuite has a way to control what the program returns,
    # and easily test all execution paths without having to maintain
    # some sources specifically designed to trigger the various
    # error conditions.
    if 'GIT_HOOKS_CVS_CHECK' in os.environ:
        cvs_check = os.environ['GIT_HOOKS_CVS_CHECK']
    else:
        cvs_check = 'cvs_check'

    # ??? It appears that cvs_check requires the SVN path to the file
    # to be checked as the first argument. Not sure why, but that does
    # not really apply in our context. Use `trunk/<module>/<path>' to
    # work around the issue.
    cvs_check_args = ['trunk/%s/%s' % (get_module_name(), filename),
                      tmp_filename]

    try:
        # In order to allow cvs_check to be a script, we need to run it
        # through a shell.  But when we do so, the Popen class no longer
        # allows us to pass the arguments as a list.  In order to avoid
        # problems with spaces or special characters, we quote the
        # arguments as needed.
        quoted_args = [quote(arg) for arg in cvs_check_args]
        out = check_output('%s %s' % (cvs_check, ' '.join(quoted_args)),
                           shell=True, stderr=STDOUT)

        # If we reach this point, it means that cvs_check returned
        # zero (success). Print any output, it might be a non-fatal
        # warning.
        if out:
            warn(*out.splitlines())

    except subprocess.CalledProcessError, E:
        debug(str(E), level=4)
        info = ["pre-commit check failed for file `%s' at commit: %s"
                % (filename, commit_rev)] \
               + E.output.splitlines()
        raise InvalidUpdate(*info)


def check_commit (old_rev, new_rev):
    """Apply pre-commit checks if appropriate.

    Raise InvalidUpdate if one or more style violation are detected.

    PARAMETERS
        old_rev: The commit to be used as a reference to determine
            the list of files that have been modified/added by
            the new commit.  May be None, in which case all files
            in new_rev will be checked.
        new_rev: The commit to be checked.
    """
    debug('check_commit(old_rev=%s, new_rev=%s)' % (old_rev, new_rev))

    if old_rev is None:
        # Get the "empty tree" special SHA1, and use that as our old tree.
        # This SHA1 is actually hard-coded in the git implementation, but
        # we recompute it each time, just in case it ever changes.
        old_rev = git.mktree(_input='')
        debug('check_commit: old_rev -> %s (empty tree SHA1)' % old_rev)

    all_changes = git.diff_tree('-r', old_rev, new_rev, _split_lines=True)
    for item in all_changes:
        (old_mode, new_mode, old_sha1, new_sha1, status, filename) \
            = item.split(None, 5)
        debug('diff-tree entry: %s %s %s %s %s %s'
              % (old_mode, new_mode, old_sha1, new_sha1, status, filename),
              level=5)

        if status in ('D'):
            debug('deleted file ignored: %s' % filename, level=2)
        elif new_mode == '160000':
            debug('subproject entry ignored: %s' % filename, level=2)
        else:
            # Note: We treat a file rename as the equivalent of the old
            # file being deleted and the new file being added. This means
            # that we should run the pre-commit checks if applicable.
            # This is why we did not tell the `git diff-tree' command
            # above to detect renames, and why we do not have a special
            # branch for status values starting with `R'.
            check_file(filename, new_sha1, new_rev)

