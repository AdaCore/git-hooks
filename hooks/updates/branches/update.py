"""Handling of branch updates."""

from fast_forward import check_fast_forward
from git import is_null_rev, git_show_ref, load_commit, commit_oneline
from updates import AbstractUpdate
from utils import InvalidUpdate, warn

BRANCH_UPDATE_EMAIL_BODY_TEMPLATE = """\
The branch '%(short_ref_name)s' was updated to point to:

 %(commit_oneline)s

It previously pointed to:

 %(old_commit_oneline)s
"""

def reject_retired_branch_update(ref_name, short_ref_name):
    """Raise InvalidUpdate if trying to update a retired branch.

    PARAMETERS:
        ref_name: The name of the branch to be updated.
        short_ref_name: The reference's short name (see short_ref_name
            attribute in class AbstractUpdate).

    REMARKS
        By convention, retiring a branch means "moving" it to the
        "retired/" sub-namespace.  Normally, it would make better
        sense to just use a tag instead of a branch (for the reference
        in "retired/"), but we allow both.
    """
    # If short_ref_name starts with "retired/", then the user is either
    # trying to create the retired branch (which is allowed), or else
    # trying to update it (which seems suspicious).  In the latter
    # case, we could disallow it, but it could also be argued that
    # updating the retired branch is sometimes useful. Keep it simple
    # for now, and allow.
    if short_ref_name.startswith('retired/'):
        return

    retired_short_ref_name = 'retired/%s' % short_ref_name
    if git_show_ref('refs/heads/%s' % retired_short_ref_name) is not None:
        raise InvalidUpdate(
            "Updates to the %s branch are no longer allowed, because"
              % short_ref_name,
            "this branch has been retired (and renamed into `%s')."
              % retired_short_ref_name)
    if git_show_ref('refs/tags/%s' % retired_short_ref_name) is not None:
        raise InvalidUpdate(
            "Updates to the %s branch are no longer allowed, because"
              % short_ref_name,
            "this branch has been retired (a tag called `%s' has been"
              % retired_short_ref_name,
            "created in its place).")


class BranchUpdate(AbstractUpdate):
    """Update object for branch creation/update."""
    def self_sanity_check(self):
        """See AbstractUpdate.self_sanity_check."""
        assert self.ref_name.startswith('refs/heads/')

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update."""
        reject_retired_branch_update(self.ref_name, self.short_ref_name)

        # Check that this is either a fast-forward update, or else that
        # forced-updates are allowed for that branch.  If old_rev is
        # null, then it's a new branch, and so fast-forward checks are
        # irrelevant.
        if not is_null_rev(self.old_rev):
            check_fast_forward(self.ref_name, self.old_rev, self.new_rev)

    def get_update_email_contents(self, email_info, added_commits,
                                  lost_commits):
        """See AbstractUpdate.get_update_email_contents.
        """
        if not self.__update_email_needed(added_commits, lost_commits):
            return None

        old_commit = load_commit(self.old_rev)
        new_commit = load_commit(self.new_rev)

        # Compute the subject.
        update_info = {'repo' : email_info.project_name,
                       'short_ref_name' : self.short_ref_name,
                       'branch' : '/%s' % self.short_ref_name,
                       'n_commits' : '',
                       'subject' : new_commit.subject[:59],
                       'old_commit_oneline' : commit_oneline(old_commit),
                       'commit_oneline' : commit_oneline(new_commit),
                      }
        if self.short_ref_name == 'master':
            update_info['branch'] = ''
        if len(added_commits) > 1:
            update_info['n_commits'] = ' (%d commits)' % len(added_commits)

        subject = "[%(repo)s%(branch)s]%(n_commits)s %(subject)s" % update_info

        body = BRANCH_UPDATE_EMAIL_BODY_TEMPLATE % update_info

        return (subject, body)


    def __update_email_needed(self, added_commits, lost_commits):
        """Return True iff the update email is needed.
        """
        # If some commits are no longer accessible from the new
        # revision (must be a non-fast-forward update), definitely
        # send an update email.
        if lost_commits:
            return True
        # If this update introduces some pre-existing commits (for
        # which individual emails are not going to be sent), send
        # the update email.
        for commit in added_commits:
            if commit.pre_existing_p:
                return True
        # Send email if there are some merge commits. ???
        return False
