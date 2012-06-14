from argparse import ArgumentParser
import re
from shutil import rmtree
import sys

from config import git_config
from fast_forward import check_fast_forward
from git import git
from pre_commit_checks import check_commit
import utils
from utils import InvalidUpdate, debug, warn, create_scratch_dir


def parse_command_line():
    """Return a namespace built after parsing the command line.
    """
    # The command-line interface is very simple, so we could possibly
    # handle it by hand.  But it's nice to have features such as
    # -h/--help switches which come for free if we use argparse.
    #
    # We use ArgumentParser, which means that we are requiring
    # Python version 2.7 or later, because it handles mandatory
    # command-line arguments for us as well.
    ap = ArgumentParser(description='Git "update" hook.')
    ap.add_argument('ref_name',
                    help='the name of the reference being updated')
    ap.add_argument('old_rev',
                    help='the SHA1 before update')
    ap.add_argument('new_rev',
                    help='the new SHA1, if the update is accepted')
    return ap.parse_args()


def is_null_rev(rev):
    """Return True iff rev is the a NULL commit SHA1.
    """
    return re.match("0+$", rev) is not None


def get_object_type(rev):
    """Determine the object type of the given commit.

    PARAMETERS
        rev: The commit SHA1 that we want to inspect.

    RETURN VALUE
        The string returned by "git cat-file -t REV", or else "delete"
        if REV is a null SHA1 (all zeroes).
    """
    if is_null_rev(rev):
        rev_type = "delete"
    else:
        rev_type = git.cat_file(rev, t=True)
    return rev_type


def find_new_branch_parent(new_rev):
    """Find the nearest commit from an already existing branch.

    The assumption is that new_rev is the commit of a new branch
    being pushed.  In that case, this function tries to find
    the commit from one of the existing branches which is nearest
    to our new_rev.

    RETURN VALUE
        The SHA1 of that parent (a string).
    """
    # For every existing branch, determine the number of commits
    # between that branch and new_rev.  Select the branch that has
    # the fewer number of commits.
    all_branches_revs = git.rev_parse(branches=True, _split_lines=True)
    (nearest_branch_rev, nearest_dist) = (None, None)
    for branch_rev in all_branches_revs:
        dist = len(git.rev_list(new_rev, '^%s' % branch_rev,
                                _split_lines=True))
        if nearest_dist is None or dist < nearest_dist:
            (nearest_branch_rev, nearest_dist) = (branch_rev, dist)

    if nearest_branch_rev is None or is_null_rev(nearest_branch_rev):
        # We did not find a parent.  This might be a headless branch...
        # Select the initial/first(=oldest) commit as the parent.
        nearest_rev = git.rev_list(new_rev, _split_lines=True)[-1]
    else:
        # We found the nearest branch.  Now, find the nearest commit.
        nearest_rev = git.merge_base(nearest_branch_rev, new_rev)

    return nearest_rev


def check_unannotated_tag(ref_name, old_rev, new_rev):
    """Do the check_update work for a new un-annotated tag.
    """
    debug('check_unannotated_tag (%s)' % ref_name)

    if git_config('hooks.allowunannotated') == "true":
        return

    # Update not permitted, raise InvalidUpdate.
    assert ref_name.startswith('refs/tags/')
    tag_name = ref_name[len('refs/tags/'):]
    raise InvalidUpdate(
        "Un-annotated tags (%s) are not allowed in this repository." % tag_name,
        "Use 'git tag [ -a | -s ]' for tags you want to propagate.")


def check_tag_deletion(ref_name, old_rev, new_rev):
    """Do the check_update work for a tag deletion.
    """
    debug('check_tag_deletion(%s)' % ref_name)

    if git_config('hooks.allowdeletetag') == "true":
        return

    # Update not permitted, raise InvalidUpdate.
    assert ref_name.startswith('refs/tags/')
    tag_name = ref_name[len('refs/tags/'):]
    raise InvalidUpdate("Deleting a tag is not allowed in this repository")


def check_branch_update(ref_name, old_rev, new_rev):
    """Do the check_update work for a branch update.
    """
    debug('check_branch_update(%s, %s, %s)' % (ref_name, old_rev, new_rev))

    if is_null_rev(old_rev):
        # A new branch is being pushed.  Determine the commit from
        # one of the existing branches which is nearest to the new
        # branch's head.
        new_branch_p = True
        old_rev = find_new_branch_parent(new_rev)
        debug('find_new_branch_parent -> %s' % old_rev)
    else:
        check_fast_forward(ref_name, old_rev, new_rev)

    if git_config('hooks.combinedstylechecking') == 'true':
        # This project prefers to perform the style check on
        # the cumulated diff, rather than commit-per-commit.
        debug('(combined style checking)')
        check_commit(old_rev, new_rev)
    else:
        debug('(commit-per-commit style checking)')
        all_commits = git.rev_list('%s..%s' % (old_rev, new_rev),
                                   reverse=True, _split_lines=True)
        for commit_id in all_commits:
            check_commit('%s^' % commit_id, commit_id)


def check_update(ref_name, old_rev, new_rev):
    """General handler of the given update.

    Raises InvalidUpdate if the update cannot be accepted (usually
    because one of the commits fails a style-check, for instance).

    PARAMETERS
        ref_name: The name of the reference being update (Eg:
            refs/heads/master).
        old_rev: The commit SHA1 of the reference before the update.
        new_rev: The new commit SHA1 that the reference will point to
            if the update is accepted.

    REMARKS
        This function assumes that utils.scratch_dir has been initialized.
    """
    debug('check_update(ref_name=%s, old_rev=%s, new_rev=%s)'
          % (ref_name, old_rev, new_rev),
          level=2)
    new_rev_type = get_object_type(new_rev)
    if ref_name.startswith('refs/tags/') and new_rev_type == 'commit':
        check_unannotated_tag(ref_name, old_rev, new_rev)
    elif ref_name.startswith('refs/tags/') and new_rev_type == 'delete':
        check_tag_deletion(ref_name, old_rev, new_rev)
    elif ref_name.startswith('refs/tags/') and new_rev_type == 'tag':
        # Pushing an annotated tag is always allowed.
        # Do we want to style-check the commits???
        pass
    elif ref_name.startswith('refs/heads/') and new_rev_type == 'commit':
        check_branch_update(ref_name, old_rev, new_rev)
    else: # pragma: no cover (should be impossible)
        raise InvalidUpdate(
            "This type of update (%s,%s) is currently unsupported."
            % (ref_name, new_rev_type))


if __name__ == "__main__":
    args = parse_command_line()
    try:
        create_scratch_dir()
        check_update(args.ref_name, args.old_rev, args.new_rev)
    except InvalidUpdate, E:
        # The update was rejected.  Print the rejection reason, and
        # exit with a nonzero status.
        warn(*E)
        sys.exit(1)
    finally:
        # Delete our scratch directory.
        if utils.scratch_dir is not None:
            rmtree(utils.scratch_dir)


