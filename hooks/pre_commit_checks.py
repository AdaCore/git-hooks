import os
import re

from config import git_config, ThirdPartyHook
from errors import InvalidUpdate
from git import git, diff_tree, file_exists
from git_attrs import git_attribute
import itertools
import utils
from utils import debug, warn

STYLE_CHECKER_CONFIG_FILE_MISSING_ERR_MSG = """\
Cannot find style_checker config file: `%(config_filename)s'.

Your repository is configured to provide a configuration file to
the style_checker; however, this configuration file (%(config_filename)s)
cannot be found in commit %(commit_rev)s.

Perhaps you haven't added this configuration file to this branch
yet?
"""


def style_check_files(filename_list, commit_rev, project_name):
    """Check a file for style violations if appropriate.

    Raise InvalidUpdate if one or more style violations are detected.

    PARAMETERS
        filename_list: The name of the file to check (an iterable).
        commit_rev: The associated commit sha1.  This piece of information
            helps us find the correct version of the files to be checked,
            as well as the .gitattributes files which are used to determine
            whether pre-commit-checks should be applied or not.
        project_name: The name of the project (same as the attribute
            in updates.emails.EmailInfo).
    """
    debug(
        "style_check_files (commit_rev=%s):\n%s"
        % (commit_rev, "\n".join([" - `%s'" % fname for fname in filename_list])),
        level=3,
    )

    config_file = git_config("hooks.style-checker-config-file")

    # Auxilary list of files we need to fetch from the same reference
    # for purposes other than checking their contents.
    aux_files = []
    if config_file is not None and config_file not in filename_list:
        if not file_exists(commit_rev, config_file):
            info = (
                STYLE_CHECKER_CONFIG_FILE_MISSING_ERR_MSG
                % {"config_filename": config_file, "commit_rev": commit_rev}
            ).splitlines()
            raise InvalidUpdate(*info)
        aux_files.append(config_file)

    # Get a copy of all the files and save them in our scratch dir.
    # In order to allow us to call the style-checker using
    # the full path (from the project's root directory) of
    # the files being checked, we re-create the path to those
    # filenames, and then copy the files at the same path.
    #
    # Providing the path as part of the filename argument is useful,
    # because it allows the messages printed by the style-checker
    # to be unambiguous in the situation where the same project
    # has multiple files sharing the same name. More generally,
    # it can also be useful to quickly locate a file in the project
    # when trying to make the needed corrections outlined by the
    # style-checker.
    for filename in itertools.chain(filename_list, aux_files):
        path_to_filename = "%s/%s" % (utils.scratch_dir, os.path.dirname(filename))
        if not os.path.exists(path_to_filename):
            os.makedirs(path_to_filename)
        git.show(
            "%s:%s" % (commit_rev, filename),
            _outfile="%s/%s" % (utils.scratch_dir, filename),
        )

    # Call the style-checker.

    # For testing purposes, provide a back-door allowing the user
    # to override the style-checking program to be used.  That way,
    # the testsuite has a way to control what the program returns,
    # and easily test all execution paths without having to maintain
    # some sources specifically designed to trigger the various
    # error conditions.
    style_checker_hook = ThirdPartyHook("hooks.style-checker")
    if "GIT_HOOKS_STYLE_CHECKER" in os.environ:
        style_checker_hook.hook_exe = os.environ["GIT_HOOKS_STYLE_CHECKER"]
    style_checker_hook_args = []
    if config_file is not None:
        style_checker_hook_args.extend(["--config", config_file])
    style_checker_hook_args.append(project_name)

    _, p, out = style_checker_hook.call(
        hook_input="\n".join(filename_list),
        hook_args=style_checker_hook_args,
        cwd=utils.scratch_dir,
    )

    if p.returncode != 0:
        info = [
            "pre-commit check failed for commit: %s" % commit_rev
        ] + out.splitlines()
        raise InvalidUpdate(*info)

    # If we reach this point, it means that the style-checker returned
    # zero (success). Print any output, it might be a non-fatal warning.
    if out:
        warn(*out.splitlines())


def ensure_iso_8859_15_only(commit):
    """Raise InvalidUpdate if the revision log contains non-ISO-8859-15 chars.

    The purpose of this check is make sure there are no unintended
    characters that snuck in, particularly non-printable characters
    accidently copy/pasted (this has been seen on MacOS X for instance,
    where the <U+2069> character was copy/pasted without the user
    even realizing it). This, in turn, can have serious unintended
    consequences, for instance when checking for ticket numbers, because
    tickets numbers need to be on a word boundary, and such invisible
    character prevents that.

    PARAMETERS
        commit: A CommitInfo object corresponding to the commit being checked.
    """
    if git_config("hooks.no-rh-character-range-check"):
        # The users of this repository explicitly requested that
        # all characters be allowed in revision logs, so do not perform
        # this verification.
        return

    for lineno, line in enumerate(commit.raw_revlog_lines, start=1):
        try:
            line.encode("ISO-8859-15")
        except UnicodeEncodeError as e:
            raise InvalidUpdate(
                "Invalid revision history for commit %s:" % commit.rev,
                "It contains characters not in the ISO-8859-15 charset.",
                "",
                "Below is the first line where this was detected"
                " (line %d):" % lineno,
                "| " + line,
                "  " + " " * e.start + "^",
                "  " + " " * e.start + "|",
                "",
                "Please amend the commit's revision history to remove it",
                "and try again.",
            )


def ensure_empty_line_after_subject(commit):
    """Raise InvalidUpdate if there is no empty line after the subject.

    More precisely, verify that if there is some text besides
    the commit subject, both parts are separated by an empty line.

    PARAMETERS
        commit: A CommitInfo object corresponding to the commit being checked.
    """
    if len(commit.raw_revlog_lines) < 2:
        # No body other than the subject.  No violation possible.
        return

    if not commit.raw_revlog_lines[1].strip() == "":
        info = (
            [
                "Invalid revision history for commit %s:" % commit.rev,
                "The first line should be the subject of the commit,",
                "followed by an empty line.",
                "",
                "Below are the first few lines of the revision history:",
            ]
            + ["| %s" % line for line in commit.raw_revlog_lines[:5]]
            + ["", "Please amend the commit's revision history and try again."]
        )
        raise InvalidUpdate(*info)


def reject_lines_too_long(commit):
    """Raise InvalidUpdate if the commit's revlog has a line that's too long.

    Does nothing if the project was configured to skip this check.

    PARAMETERS
        commit: A CommitInfo object corresponding to the commit being checked.
    """
    max_line_length = git_config("hooks.max-rh-line-length")
    if max_line_length <= 0:
        # A value of zero (or less) means that the project does not
        # want this check to be applied.  Skip it.
        return

    for line in commit.raw_revlog_lines:
        if len(line) > max_line_length:
            raise InvalidUpdate(
                "Invalid revision history for commit %s:" % commit.rev,
                "",
                "The following line in the revision history is too long",
                "(%d characters, when the maximum is %d characters):"
                % (len(line), max_line_length),
                "",
                ">>> %s" % line,
            )


def reject_unedited_merge_commit(commit):
    """Raise InvalidUpdate if the commit looks like an unedited merge commit.

    More precisely, we are trying to catch the cases where a merge
    was performed without the user being aware of it.  This can
    happen for instance if the user typed "git pull" instead of
    "git pull --rebase".

    We implement a very crude identification mechanism at the moment,
    based on matching the default revision history for merge commits.

    If the merge commit was intended, the user is expected to provide
    a non-default revision history, thus satisfying this check.

    PARAMETERS
        commit: A CommitInfo object corresponding to the commit being checked.
    """
    if git_config("hooks.disable-merge-commit-checks"):
        # The users of this repository do not want this safety guard.
        # So do not perform this check.
        return

    # We have seen cases (with git version 1.7.10.4), where the default
    # revision history for a merge commit is just: "Merge branch 'xxx'.".
    RH_PATTERN = "Merge branch '.*'"

    for line in commit.raw_revlog_lines:
        if re.match(RH_PATTERN, line):
            info = [
                'Pattern "%s" has been detected.' % RH_PATTERN,
                "(in commit %s)" % commit.rev,
                "",
                "This usually indicates an unintentional merge commit.",
                "If you would really like to push a merge commit," " please",
                "edit the merge commit's revision history.",
            ]
            raise InvalidUpdate(*info)


def reject_merge_conflict_section(commit):
    """Raise InvalidUpdate if the commit's revlog contains "Conflicts:" in it.

    More precisely, we are trying to catch the cases where a user
    performed a merge which had conflicts, resolved them, but then
    forgot to remove the "Conflicts:" section provided in the default
    revision history when creating the commit.

    PARAMETERS
        commit: A CommitInfo object corresponding to the commit being checked.
    """
    RH_PATTERN = "Conflicts:"

    for line in commit.raw_revlog_lines:
        if line.strip() == RH_PATTERN:
            info = [
                'Pattern "%s" has been detected.' % RH_PATTERN,
                "(in commit %s)" % commit.rev,
                "",
                "This usually indicates a merge commit where some" " merge conflicts",
                'had to be resolved, but where the "Conflicts:"' " section has not ",
                "been deleted from the revision history.",
                "",
                "Please edit the commit's revision history to" " either delete",
                "the section, or to avoid using the pattern above" " by itself.",
            ]
            raise InvalidUpdate(*info)


def check_missing_ticket_number(commit):
    """Raise InvalidUpdate if a TN in the commit's revlog is missing...

    Note: This only applies if the project is configured to require TNs.

    PARAMETERS
        commit: A CommitInfo object corresponding to the commit being checked.
    """
    if not git_config("hooks.tn-required"):
        return

    tn_re = [  # Satisfy pep8's 2-spaces before inline comment.
        # The word 'no-tn-check' anywhere in the RH removes the need
        # for a TN in the RH.
        r"\bno-tn-check\b",
        # TN regexp.
        r"\b[0-9A-Z][0-9A-Z][0-9][0-9]-[0-9A-Z][0-9][0-9]\b",
    ]
    for line in commit.raw_revlog_lines:
        if re.search("|".join(tn_re), line, re.IGNORECASE):
            return

    raise InvalidUpdate(
        *[
            "The following commit is missing a ticket number inside",
            "its revision history.  If the change is sufficiently",
            "minor that a ticket number is not meaningful, please use",
            'the word "no-tn-check" in place of a ticket number.',
            "",
            "commit %s" % commit.rev,
            "Subject: %s" % commit.subject,
        ]
    )


def check_revision_history(commit):
    """Apply pre-commit checks to the commit's revision history.

    Raise InvalidUpdate if one or more style violation are detected.

    PARAMETERS
        commit: A CommitInfo object representing the commit to be checked.
    """
    if "no-rh-check" in commit.raw_revlog:
        return

    # Various checks on the revision history...
    ensure_iso_8859_15_only(commit)
    ensure_empty_line_after_subject(commit)
    reject_lines_too_long(commit)
    reject_unedited_merge_commit(commit)
    reject_merge_conflict_section(commit)
    check_missing_ticket_number(commit)


def check_filename_collisions(commit):
    """raise InvalidUpdate if the name of two files only differ in casing.

    PARAMETERS
        commit: A CommitInfo object representing the commit to be checked.
    """
    filename_map = {}
    for filename in commit.all_files():
        key = filename.lower()
        if key not in filename_map:
            filename_map[key] = [filename]
        else:
            filename_map[key].append(filename)
    collisions = [
        filename_map[k] for k in filename_map.keys() if len(filename_map[k]) > 1
    ]
    if collisions:
        info = [
            "The following filename collisions have been detected.",
            "These collisions happen when the name of two or more files",
            'differ in casing only (Eg: "hello.txt" and "Hello.txt").',
            "Please re-do your commit, chosing names that do not collide.",
            "",
            "    Commit: %s" % commit.rev,
            "    Subject: %s" % commit.subject,
            "",
            "The matching files are:",
        ]
        for matching_names in sorted(collisions):
            info.append("")  # Empty line to separate each group...
            info += ["    %s" % filename for filename in sorted(matching_names)]
        raise InvalidUpdate(*info)


def check_filepath_length(commit):
    """Raise InvalidUpdate if the commit introduces files with a name too long.

    PARAMETERS
        commit: A CommitInfo object representing the commit to be checked.
    """
    max_path_length = git_config("hooks.max-filepath-length")
    if max_path_length <= 0:
        # This means the project explicitly requested that this check
        # be skipped.
        return

    too_long = [
        file_path
        for file_path in commit.added_files()
        if len(file_path) > max_path_length
    ]
    if too_long:
        info = [
            "The following commit introduces some new files whose total",
            "path length exceeds the maximum allowed for this repository.",
            "Please re-do your commit choosing shorter paths for those new",
            "files, or contact your repository administrator if you believe",
            "the limit should be raised.",
            "",
            "    Commit: {commit.rev}".format(commit=commit),
            "    Subject: {commit.subject}".format(commit=commit),
            "",
            "The problematic files are ({max_path_length} characters max):".format(
                max_path_length=max_path_length
            ),
            "",
        ]
        info.extend(
            "    {path_name} ({path_len} characters)".format(
                path_name=path_name, path_len=len(path_name)
            )
            for path_name in too_long
        )
        info.append("")
        raise InvalidUpdate(*info)


MERGE_NOT_ALLOWED_ERROR_MSG = """\
Merge commits are not allowed on %(ref_name)s.
The commit that caused this error is:

    commit %(rev)s
    Subject: %(subject)s

Hint: Consider using "git cherry-pick" instead of "git merge",
      or "git pull --rebase" instead of "git pull".
"""


def reject_commit_if_merge(commit, ref_name):
    """Raise InvalidUpdate if commit is a merge commit.

    Raises an assertion failure if commit.parent_revs is not None
    (see PARAMETERS for meore info on this parameter's type).

    PARAMETERS
        commit: A CommitInfo object.
        ref_name: The name of the reference being updated.
    """
    assert commit.parent_revs is not None
    if len(commit.parent_revs) > 1:
        raise InvalidUpdate(
            *(
                MERGE_NOT_ALLOWED_ERROR_MSG
                % {"ref_name": ref_name, "rev": commit.rev, "subject": commit.subject}
            ).splitlines()
        )


def style_check_commit(old_rev, new_rev, project_name):
    """Call check_file for every file changed between old_rev and new_rev.

    Raise InvalidUpdate if one or more style violation are detected.

    PARAMETERS
        old_rev: The commit to be used as a reference to determine
            the list of files that have been modified/added by
            the new commit.  Must be a valid revision.
        new_rev: The commit to be checked.
        project_name: The name of the project (same as the attribute
            in updates.emails.EmailInfo).
    """
    debug("style_check_commit(old_rev=%s, new_rev=%s)" % (old_rev, new_rev))

    # We allow users to explicitly disable pre-commit checks for
    # specific commits via the use of a special keyword placed anywhere
    # in the revision log. If found, then return immediately.
    raw_revlog = git.log("-1", new_rev, pretty="format:%B", _decode=True)
    if "no-precommit-check" in raw_revlog:
        debug("pre-commit checks explicity disabled for commit %s" % new_rev)
        return

    changes = diff_tree("-r", old_rev, new_rev)
    files_to_check = []

    for item in changes:
        (old_mode, new_mode, old_sha1, new_sha1, status, filename) = item
        debug(
            "diff-tree entry: %s %s %s %s %s %s"
            % (old_mode, new_mode, old_sha1, new_sha1, status, filename),
            level=5,
        )

        if status in ("D"):
            debug("deleted file ignored: %s" % filename, level=2)
        elif new_mode == "160000":
            debug("subproject entry ignored: %s" % filename, level=2)
        else:
            # Note: We treat a file rename as the equivalent of the old
            # file being deleted and the new file being added. This means
            # that we should run the pre-commit checks if applicable.
            # This is why we did not tell the `git diff-tree' command
            # above to detect renames, and why we do not have a special
            # branch for status values starting with `R'.
            files_to_check.append(filename)

    no_style_check_map = git_attribute(new_rev, files_to_check, "no-precommit-check")

    def needs_style_check_p(filename):
        """Return True if the file should be style-checked, False otherwise.

        In addition to returning True/False, it generates a debug log
        when the file does have a no-precommit-check attribute.
        """
        if no_style_check_map[filename] == "set":
            debug("no-precommit-check: %s commit_rev=%s" % (filename, new_rev))
            return False
        else:
            return True

    files_to_check = tuple(filter(needs_style_check_p, files_to_check))
    if not files_to_check:
        debug("style_check_commit: no files to style-check")
        return

    style_check_files(files_to_check, new_rev, project_name)
