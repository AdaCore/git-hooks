"""Branch updates root module."""

from git import git
from utils import debug

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
