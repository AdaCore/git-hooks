"""Handling of branch deletion."""

from git import commit_oneline
from updates import AbstractUpdate

BRANCH_DELETION_EMAIL_BODY_TEMPLATE = """\
The branch '%(short_ref_name)s' was deleted.
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

    def get_update_email_contents(self, email_info, added_commits,
                                  lost_commits):
        """See AbstractUpdate.get_update_email_contents.
        """
        subject = "[%s] Deleted branch %s" % (email_info.project_name,
                                              self.short_ref_name)

        update_info = {'short_ref_name' : self.short_ref_name,
                       'commit_oneline' : commit_oneline(self.old_rev),
                      }
        body = BRANCH_DELETION_EMAIL_BODY_TEMPLATE % update_info

        return (subject, body)
