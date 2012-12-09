"""Management of git references in a git repository.
"""
from git import git, git_show_ref, is_null_rev
from utils import debug


class GitReferences(object):
    """A class to manipulate a "list" of references and their values.

    ATTRIBUTES
        refs: A dictionary, as described in git_show_ref.
    """
    def __init__(self, *args, **kwargs):
        """The constructor.

        PARAMETERS
            All parameters except self are passed as is to git_show_ref,
            and the result is used to set the self.refs attribute.
        """
        self.refs = git_show_ref(*args, **kwargs)

    def update_ref(self, ref_name, new_rev):
        """Update ref_name's value.

        PARAMETERS
            ref_name: The name of the reference to update.
            new_rev: The reference's new value (a null value means that
                the reference is being removed, and thus will result
                in the associated entry to be removed as well).
        """
        if is_null_rev(new_rev):
            del(self.refs[ref_name])
        else:
            self.refs[ref_name] = new_rev

    def new_commits(self, new_rev):
        """Return a list of new commits introduced by the update.

        This function searches the "nearest" commit from one of
        the references that already exist in the repository, and
        then generates a list of commits, starting with that "nearest"
        commit.  The list contains all the new commits leading to
        new_rev, in "chronological" order (parents first).

        If new_rev is a new headless branch with no common ancestor,
        then there is no "nearest" commit, and the first element of
        the list is set to None.

        PARAMETERS
            new_rev: The reference's new rev (SHA1).

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
        nearest_rev = None

        # For every existing reference, determine the number of commits
        # between that reference and new_rev.  Select the reference which
        # has the fewer number of commits.
        for (_, rev) in self.refs.items():
            rev_list_to_new_rev = git.rev_list(new_rev, '^%s' % rev,
                                               reverse=True,
                                               _split_lines=True)
            if len(rev_list_to_new_rev) < len(commit_list):
                nearest_rev = rev
                commit_list = rev_list_to_new_rev

        # If we found an already-existing reference that has common
        # ancestors with our new commit, then insert that common
        # commit at the start of our commit list.
        if nearest_rev is not None:
            commit_list.insert(0, git.merge_base(nearest_rev, new_rev))
        else:
            # This is most likely a new headless branch. Use None as
            # our convention to mean that the oldest commit is a root
            # commit (it has no parent).
            commit_list.insert(0, None)
        debug('update base: %s' % commit_list[0])

        return commit_list
