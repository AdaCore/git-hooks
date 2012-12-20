"""Handling of branch creation."""

from git import commit_oneline
from updates.branches.update import BranchUpdate

BRANCH_CREATION_EMAIL_BODY_TEMPLATE = """\
The branch '%(short_ref_name)s' was created pointing to:

 %(commit_oneline)s"""

class BranchCreation(BranchUpdate):
    """Update class for branch creation.

    REMARKS
        Creation is a special case of update, and the implementation of
        some of the abstract methods would be identical.  So inherit
        from BranchUpdate.
    """
    def get_update_email_contents(self, email_info, added_commits,
                                  lost_commits):
        """See AbstractUpdate.get_update_email_contents.
        """
        subject = "[%s] Created branch %s" % (email_info.project_name,
                                              self.short_ref_name)

        update_info = {'short_ref_name' : self.short_ref_name,
                       'commit_oneline' : commit_oneline(self.new_rev),
                      }
        body = BRANCH_CREATION_EMAIL_BODY_TEMPLATE % update_info
        if self.summary_of_changes_needed(added_commits, lost_commits):
            body += self.summary_of_changes(added_commits, lost_commits)

        return (subject, body)
