"""Management of git references in a git repository.
"""
from git import (git, git_show_ref, is_null_rev, rev_list_commits,
                 load_commit, commit_parents, GitCommit)
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

    def expand(self, old_rev, new_rev):
        """Return a list of new commits introduced by the update.

        This function expands old_rev..new_rev into a list of
        GitCommit objects, where each GitCommit object has an
        additional attribute called new_in_repo, set to True
        iff the commit is new for this repository.

        If old_rev is null, then this function tries to compute one
        by using the nearest commit from one of the references
        that exist already.  If new_rev is a new headless reference
        with no common ancestor, then there is no "nearest" commit,
        and the first element of the list is a GitCommit object
        whose rev and subject are set to None.

        The list is sorted in chronological order.

        PARAMETERS
            old_rev: The reference's old rev (SHA1).
            new_rev: The reference's new rev (SHA1).

        RETURN VALUE
            A list of commits.  The list will always contain at least
            one element, which is the "update base" commit (the commit
            that is common to an already-existing branch an our new_rev).
            The revision and subject of the "update base" may be None.
        """
        if is_null_rev(new_rev):
            return [None]

        exclude = ['^%s' % self.refs[ref_name]
                   for ref_name in self.refs.keys()]

        # Compute the list of commits that are not accessible from
        # any of the references.  These are the commits which are
        # new in the repository.
        #
        # Note that we do not use the rev_list_commits function for
        # that, because we only need the commit hashes, and a list
        # of commit hashes is more convenient for what we want to do
        # than a list of GitCommit objects.
        new_repo_revs = git.rev_list(new_rev, *exclude, reverse=True,
                                     _split_lines=True)

        # If this is a reference creation (old_rev is null), try to
        # find a commit which can serve as old_rev.  We try to find
        # a pre-existing commit making the old_rev..new_rev list
        # as short as possible.
        if is_null_rev(old_rev):
            if len(new_repo_revs) > 0:
                # The ref update brings some new commits.  The first
                # parent of the oldest of those commits, if it exists,
                # seems like a good candidate.  If it does not exist,
                # we are pushing a entirely new headless branch, and
                # old_rev should remain null.
                parents = commit_parents(new_repo_revs[0])
                if parents is not None:
                    old_rev = parents[0]
            else:
                # This reference update does not bring any new commits
                # at all. This means new_rev is already accessible
                # through one of the references, thus making it a good
                # old_rev as well.
                old_rev = new_rev

        # Expand old_rev..new_rev to compute the list of commits which
        # are new for the reference.  If there is no actual old_rev
        # (Eg. a headless branch), then expand to all commits accessible
        # from that reference.
        if not is_null_rev(old_rev):
            commit_list = rev_list_commits(new_rev, '^%s' % old_rev,
                                           reverse=True)
            commit_list.insert(0, load_commit(old_rev))
        else:
            commit_list = rev_list_commits(new_rev, reverse=True)
            commit_list.insert(0, GitCommit(None, None))

        # Iterate over every commit, and mark them as either "new"
        # for the repo or not.
        for commit in commit_list:
            commit.new_in_repo = commit.rev in new_repo_revs

        debug('update base: %s' % commit_list[0].rev)

        return commit_list
