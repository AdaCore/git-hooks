"""Handling of branch deletion."""

from git import commit_oneline
from updates import AbstractUpdate
from updates.branches import branch_summary_of_changes_needed

BRANCH_DELETION_EMAIL_BODY_TEMPLATE = """\
The branch %(human_readable_ref_name)s was deleted.
It previously pointed to:

 %(commit_oneline)s"""


class BranchDeletion(AbstractUpdate):
    """Update object for branch creation/update."""
    def self_sanity_check(self):
        """See AbstractUpdate.self_sanity_check."""
        assert self.ref_name.startswith('refs/heads/')

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update."""
        # Deleting a branch is always allowed.
        pass

    def get_update_email_contents(self):
        """See AbstractUpdate.get_update_email_contents.
        """
        subject = "[%s] Deleted branch %s" % (
            self.email_info.project_name,
            self.human_readable_ref_name())

        update_info = {
            'human_readable_ref_name': self.human_readable_ref_name(),
            'commit_oneline': commit_oneline(self.old_rev),
            }
        body = BRANCH_DELETION_EMAIL_BODY_TEMPLATE % update_info
        if branch_summary_of_changes_needed(self.added_commits,
                                            self.lost_commits):
            body += self.summary_of_changes()

        return (self.everyone_emails(), subject, body)
