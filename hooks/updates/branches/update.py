"""Handling of branch updates."""

from errors import InvalidUpdate
from fast_forward import check_fast_forward
from git import is_null_rev, commit_oneline, commit_subject
from updates import AbstractUpdate, RefKind
from updates.branches import branch_summary_of_changes_needed

BRANCH_UPDATE_EMAIL_BODY_TEMPLATE = """\
The branch '%(short_ref_name)s' was updated to point to:

 %(commit_oneline)s

It previously pointed to:

 %(old_commit_oneline)s"""


def reject_retired_branch_update(short_ref_name, all_refs):
    """Raise InvalidUpdate if trying to update a retired branch.

    PARAMETERS:
        short_ref_name: The reference's short name (see short_ref_name
            attribute in class AbstractUpdate).
        all_refs: See the all_refs attribute in class AbstractUpdate.

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
    if 'refs/heads/%s' % retired_short_ref_name in all_refs:
        raise InvalidUpdate(
            "Updates to the %s branch are no longer allowed, because"
            % short_ref_name,
            "this branch has been retired (and renamed into `%s')."
            % retired_short_ref_name)
    if 'refs/tags/%s' % retired_short_ref_name in all_refs:
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
        assert self.ref_kind == RefKind.branch_ref \
            and self.object_type == 'commit'

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update."""
        reject_retired_branch_update(self.short_ref_name,
                                     self.all_refs)

        # Check that this is either a fast-forward update, or else that
        # forced-updates are allowed for that branch.  If old_rev is
        # null, then it's a new branch, and so fast-forward checks are
        # irrelevant.
        if not is_null_rev(self.old_rev):
            check_fast_forward(self.ref_name, self.old_rev, self.new_rev)

    def get_update_email_contents(self):
        """See AbstractUpdate.get_update_email_contents.
        """
        # For branch updates, we only send the update email when
        # the summary of changes is needed.
        if not branch_summary_of_changes_needed(self.new_commits_for_ref,
                                                self.lost_commits):
            return None

        # Compute the subject.
        update_info = {'repo': self.email_info.project_name,
                       'short_ref_name': self.short_ref_name,
                       'branch': '/%s' % self.short_ref_name,
                       'n_commits': '',
                       'subject': commit_subject(self.new_rev)[:59],
                       'old_commit_oneline': commit_oneline(self.old_rev),
                       'commit_oneline': commit_oneline(self.new_rev),
                       }
        if self.short_ref_name == 'master':
            update_info['branch'] = ''
        if len(self.new_commits_for_ref) > 1:
            update_info['n_commits'] = \
                ' (%d commits)' % len(self.new_commits_for_ref)

        subject = "[%(repo)s%(branch)s]%(n_commits)s %(subject)s" % update_info

        body = BRANCH_UPDATE_EMAIL_BODY_TEMPLATE % update_info
        body += self.summary_of_changes()

        return (self.everyone_emails(), subject, body)
