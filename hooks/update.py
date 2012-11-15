from argparse import ArgumentParser
import re
from shutil import rmtree
import sys

from config import git_config
from fast_forward import check_fast_forward
from git import git, is_null_rev, get_object_type, git_show_ref
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


def reject_retired_branch_update(ref_name):
    """Raise InvalidUpdate if trying to update a retired branch.

    PARAMETERS:
        ref_name: The name of the branch to be updated.

    REMARKS
        By convention, retiring a branch means "moving" it to the
        "retired/" sub-namespace.  Normally, it would make better
        sense to just use a tag instead of a branch (for the reference
        in "retired/"), but we allow both.
    """

    assert ref_name.startswith('refs/heads/')
    short_name = ref_name[len('refs/heads/'):]

    # If short_name starts with "retired/", then the user is either
    # trying to create the retired branch (which is allowed), or else
    # trying to update it (which seems suspicious).  In the latter
    # case, we could disallow it, but it could also be argued that
    # updating the retired branch is sometimes useful. Keep it simple
    # for now, and allow.

    retired_short_name = 'retired/%s' % short_name
    if git_show_ref('refs/heads/%s' % retired_short_name) is not None:
        raise InvalidUpdate(
            "Updates to the %s branch are no longer allowed, because"
              % short_name,
            "this branch has been retired (and renamed into `%s')."
              % retired_short_name)
    if git_show_ref('refs/tags/%s' % retired_short_name) is not None:
        raise InvalidUpdate(
            "Updates to the %s branch are no longer allowed, because"
              % short_name,
            "this branch has been retired (a tag called `%s' has been"
              % retired_short_name,
            "created in its place).")

def warn_about_tag_update(tag_name, old_rev, new_rev):
    """Emit a warning about tag updates.

    PARAMETER
        tag_name: The name of the tag being updated.
        old_rev: The old revision referenced by the tag.
        new_rev: The new revision referenced by the tag.
    """
    warn('---------------------------------------------------------------',
         '--  IMPORTANT NOTICE:',
         '--',
         '--  You just updated the "%s" tag as follow:' % tag_name,
         '--    old SHA1: %s' % old_rev,
         '--    new SHA1: %s' % new_rev,
         '--',
         '-- Other developers pulling from this repository will not',
         '-- get the new tag. Assuming this update was deliberate,',
         '-- notifying all known users of the update is recommended.',
         '---------------------------------------------------------------')


def expand_new_commit_to_list(new_rev):
    """Expand the new commit into a list of commits introduced by the update.

    This function searches the "nearest" commit from one of the branches
    that already exist in the repository, and then generates a list of
    commits, starting with that "nearest" commit.  The list contains
    all the new commits leading to new_rev, in "chronological" order
    (parents first).

    If new_rev is a new headless branch with no common ancestor, then
    there is no "nearest" commit, and the first element of the list
    is set to None.

    REMARKS
        We treat branch updates different from new branches (where
        the old_rev is the null SHA), because branch updates can be
        non-fast-forward updates.  With such updates, the branch
        become completely unrelated to the old branch, or even
        an entirely new and headless branch, not connected to any
        of the already existing branches.  We could use simplified
        code for the easy fast-forward update, but that would be
        extra code to maintain.

    RETURN VALUE
        A list of commits.  The list will always contain at least
        one element, which is the "update base" commit (the commit
        that is common to an already-existing branch an our new_rev),
        or None.
    """
    # Start from the entire list of commits for our new branch, and
    # see if we can shorten that list a bit by finding an already
    # existing branch that has commits in common.
    commit_list = git.rev_list(new_rev, reverse=True, _split_lines=True)
    nearest_branch_rev = None

    # For every existing branch, determine the number of commits
    # between that branch and new_rev.  Select the branch that has
    # the fewer number of commits.
    all_branches_revs = git.rev_parse(branches=True, _split_lines=True)
    for branch_rev in all_branches_revs:
        rev_list_to_branch = git.rev_list(new_rev, '^%s' % branch_rev,
                                          reverse=True, _split_lines=True)
        if len(rev_list_to_branch) < len(commit_list):
            nearest_branch_rev = branch_rev
            commit_list = rev_list_to_branch

    # If we found an already-existing branch that has common
    # ancestors with our new branch, then insert that common
    # commit at the start of our commit list.
    if nearest_branch_rev is not None:
        commit_list.insert(0, git.merge_base(nearest_branch_rev, new_rev))
    else:
        # This is most likely a new headless branch. Use None as
        # our convention to mean that the oldest commit is a root
        # commit (it has no parent).
        commit_list.insert(0, None)
    debug('update base: %s' % commit_list[0])

    return commit_list


def check_unannotated_tag(ref_name, old_rev, new_rev):
    """Do the check_update work for a new un-annotated tag.
    """
    debug('check_unannotated_tag (%s)' % ref_name)

    assert ref_name.startswith('refs/tags/')
    tag_name = ref_name[len('refs/tags/'):]

    # If lightweight tags are not allowed, refuse the update.
    if git_config('hooks.allowunannotated') != "true":
        raise InvalidUpdate(
            "Un-annotated tags (%s) are not allowed in this repository."
                % tag_name,
            "Use 'git tag [ -a | -s ]' for tags you want to propagate.")

    # If this is a pre-existing tag being updated, there are pitfalls
    # that the user should be warned about.
    if not is_null_rev(old_rev) and not is_null_rev(new_rev):
        warn_about_tag_update(tag_name, old_rev, new_rev)


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


def check_tag_update(ref_name, old_rev, new_rev):
    """Do the check_update work for a tag update (or creation).

    REMARKS
        Pushing an annotated tag is always allowed.
        Do we want to style-check the commits???
    """
    assert ref_name.startswith('refs/tags/')
    tag_name = ref_name[len('refs/tags/'):]

    # If this is a pre-existing tag being updated, there are pitfalls
    # that the user should be warned about.
    if not is_null_rev(old_rev) and not is_null_rev(new_rev):
        warn_about_tag_update(tag_name, old_rev, new_rev)


def check_branch_update(ref_name, old_rev, new_rev):
    """Do the check_update work for a branch update.
    """
    debug('check_branch_update(%s, %s, %s)' % (ref_name, old_rev, new_rev))

    reject_retired_branch_update(ref_name)

    # Check that this is either a fast-forward update, or else that
    # forced-updates are allowed for that branch.  If old_rev is
    # null, then it's a new branch, and so fast-forward checks are
    # irrelevant.
    if not is_null_rev(old_rev):
        check_fast_forward(ref_name, old_rev, new_rev)

    all_commits = expand_new_commit_to_list(new_rev)
    if len(all_commits) < 2:
        # There are no new commits, so nothing further to check.
        # Note: We check for len < 2 instead of 1, since the first
        # element is the "update base" commit (similar to the merge
        # base, where the commit is the common commit between 2 branches).
        return

    if git_config('hooks.combinedstylechecking') == 'true':
        # This project prefers to perform the style check on
        # the cumulated diff, rather than commit-per-commit.
        debug('(combined style checking)')
        all_commits = (all_commits[0], all_commits[-1])
    else:
        debug('(commit-per-commit style checking)')

    # Iterate over our list of commits in pairs...
    for (parent_rev, rev) in zip(all_commits[:-1], all_commits[1:]):
        check_commit(parent_rev, rev)


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
        check_tag_update(ref_name, old_rev, new_rev)
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


