import os
from os.path import basename
from pipes import quote
import re
import subprocess
from subprocess import check_output, STDOUT

from config import git_config
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


def ensure_empty_line_after_subject(rev, raw_rh):
    """Raise InvalidUpdate if there is no empty line after the subject.

    More precisely, verify that if there is some text besides
    the commit subject, both parts are separated by an empty line.

    PARAMETERS
        rev: The revision of the commit being checked.
        raw_rh: A list of lines corresponding to the raw revision
            history (as opposed to the revision history as usually
            displayed by git where the subject lines are wrapped).
            See --pretty format option "%B" for more details.
    """
    if len(raw_rh) < 2:
        # No body other than the subject.  No violation possible.
        return

    if not raw_rh[1].strip() == '':
        info = ['Invalid revision history for commit %s:' % rev,
                'The first two lines should be the subject of the commit,',
                'followed by an empty line.',
                '',
                'Below are the first few lines of the revision history:'] \
                + [ '| %s' % line for line in raw_rh[:5]] \
                + ['',
                   "Please amend the commit's revision history and try again."]
        raise InvalidUpdate(*info)


def reject_unedited_merge_commit(rev, raw_rh):
    """Raise InvalidUpdate if raw_rh looks like an unedited merge commit's RH.

    More precisely, we are trying to catch the cases where a merge
    was performed without the user being aware of it.  This can
    happen for instance if the user typed "git pull" instead of
    "git pull --rebase".

    We implement a very crude identification mechanism at the moment,
    based on matching the default revision history for merge commits.

    If the merge commit was intended, the user is expected to provide
    a non-default revision history, thus satisfying this check.

    PARAMETERS
        rev: The revision of the commit being checked.
        raw_rh: A list of lines corresponding to the raw revision
            history (as opposed to the revision history as usually
            displayed by git where the subject lines are wrapped).
            See --pretty format option "%B" for more details.
    """
    # We have seen cases (with git version 1.7.10.4), where the default
    # revision history for a merge commit is just: "Merge branch 'xxx'.".
    RH_PATTERN = "Merge branch '.*'"

    for line in raw_rh:
        if re.match(RH_PATTERN, line):
            info = ['Pattern "%s" has been detected.' % RH_PATTERN,
                    '(in commit %s)' % rev,
                    '',
                    'This usually indicates an unintentional merge commit.',
                    'If you would really like to push a merge commit,'
                        ' please',
                    "edit the merge commit's revision history."]
            raise InvalidUpdate(*info)


def reject_merge_conflict_section(rev, raw_rh):
    """Raise InvalidUpdate if raw_rh contains "Conflicts:" in it.

    More precisely, we are trying to catch the cases where a user
    performed a merge which had conflicts, resolved them, but then
    forgot to remove the "Conflicts:" section provided in the default
    revision history when creating the commit.

    PARAMETERS
        rev: The revision of the commit being checked.
        raw_rh: A list of lines corresponding to the raw revision
            history (as opposed to the revision history as usually
            displayed by git where the subject lines are wrapped).
            See --pretty format option "%B" for more details.
    """
    RH_PATTERN = "Conflicts:"

    for line in raw_rh:
        if line.strip() == RH_PATTERN:
            info = ['Pattern "%s" has been detected.' % RH_PATTERN,
                    '(in commit %s)' % rev,
                    '',
                    'This usually indicates a merge commit where some'
                        ' merge conflicts',
                    'had to be resolved, but where the "Conflicts:"'
                        ' section has not ',
                    'been deleted from the revision history.',
                    '',
                    'Please edit the commit\'s revision history to'
                        ' either delete',
                    'the section, or to avoid using the pattern above'
                        ' by itself.']
            raise InvalidUpdate(*info)


def check_missing_ticket_number(rev, raw_rh):
    """Raise InvalidUpdate if a TN in the RH is missing...

    Note: This only applies if the project is configured to require TNs.

    PARAMETERS
        rev: The revision of the commit being checked.
        raw_rh: A list of lines corresponding to the raw revision
            history (as opposed to the revision history as usually
            displayed by git where the subject lines are wrapped).
            See --pretty format option "%B" for more details.
    """
    if git_config('hooks.tn-required') != 'true':
        return

    tn_re = [# The word 'minor' (as in "Minor reformatting")
             # anywhere in the RH removes the need for a TN
             # in the RH.
             r'\bminor\b',
             # Same for '(no-tn-check)'.
             r'\(no-tn-check\)',
             # TN regexp.
             '[0-9A-Z][0-9A-Z][0-9][0-9]-[0-9A-Z][0-9][0-9]',
            ]
    for line in raw_rh:
        if re.search('|'.join(tn_re), line, re.IGNORECASE):
            return

    raise InvalidUpdate(*[
        'The following commit is missing a ticket number inside',
        'its revision history.  If the change is sufficiently',
        'minor that a ticket number is not meaningful, please use',
        'either the word "Minor" or the "(no-tn-check)" string',
        'in place of a ticket number.',
        '',
        'commit %s' % rev,
        'Subject: %s' % raw_rh[0]
        ])


def check_commit(old_rev, new_rev):
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

    # Various checks on the revision history...
    raw_body = git.log(new_rev, max_count='1', pretty='format:%B',
                       _split_lines=True)
    ensure_empty_line_after_subject(new_rev, raw_body)
    reject_unedited_merge_commit(new_rev, raw_body)
    reject_merge_conflict_section(new_rev, raw_body)
    check_missing_ticket_number(new_rev, raw_body)

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

