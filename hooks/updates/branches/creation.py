"""Handling of branch creation."""

from git import commit_oneline
from updates.branches import branch_summary_of_changes_needed
from updates.branches.update import BranchUpdate

BRANCH_CREATION_EMAIL_BODY_TEMPLATE = """\
The branch '%(short_ref_name)s' was created%(in_namespace)s pointing to:

 %(commit_oneline)s"""


class BranchCreation(BranchUpdate):
    """Update class for branch creation.

    REMARKS
        Creation is a special case of update, and the implementation of
        some of the abstract methods would be identical.  So inherit
        from BranchUpdate.
    """
    def get_update_email_contents(self):
        """See AbstractUpdate.get_update_email_contents.
        """
        # For branches, reference names normally start with refs/heads/.
        # If that's not the case, make the branch's namespace explicit.
        if self.ref_namespace in (None, 'refs/heads'):
            in_namespace = ''
        else:
            in_namespace = " in namespace '%s'" % self.ref_namespace

        subject = "[%s] Created branch '%s'%s" % (self.email_info.project_name,
                                                  self.short_ref_name,
                                                  in_namespace,)

        update_info = {'short_ref_name': self.short_ref_name,
                       'commit_oneline': commit_oneline(self.new_rev),
                       'in_namespace': in_namespace,
                       }
        body = BRANCH_CREATION_EMAIL_BODY_TEMPLATE % update_info
        if branch_summary_of_changes_needed(self.added_commits,
                                            self.lost_commits):
            body += self.summary_of_changes()

        return (subject, body)
