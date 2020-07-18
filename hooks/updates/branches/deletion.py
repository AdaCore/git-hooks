"""Handling of branch deletion."""

from config import git_config
from errors import InvalidUpdate
from git import commit_oneline
from updates import AbstractUpdate, RefKind
from updates.branches import branch_summary_of_changes_needed

BRANCH_DELETION_EMAIL_BODY_TEMPLATE = """\
The branch %(human_readable_ref_name)s was deleted.
It previously pointed to:

 %(commit_oneline)s"""

DEFAULT_REJECTED_BRANCH_DELETION_TIP = """\
If you are trying to delete a branch which was created
by mistake, contact an administrator, and ask him to
temporarily change the repository's configuration
so the branch can be deleted (he may elect to delete
the branch himself to avoid the need to coordinate
the operation)."""


class BranchDeletion(AbstractUpdate):
    """Update object for branch creation/update."""
    def self_sanity_check(self):
        """See AbstractUpdate.self_sanity_check."""
        assert self.ref_kind == RefKind.branch_ref \
            and self.object_type == 'commit'

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update."""
        if (
            git_config("hooks.restrict-branch-deletion")
            and self.search_config_option_list(
                option_name="hooks.allow-delete-branch", ref_name=self.ref_name
            )
            is None
        ):
            # The repository is configured to restrict branch deletion
            # and the reference is not in the list of references that
            # are allowed to be deleted. Reject the update with a helpful
            # error message.
            err = []

            allowed_list = git_config("hooks.allow-delete-branch")
            if not allowed_list:
                err.append(
                    "Deleting branches is not allowed for this repository."
                )

            else:
                err.extend(
                    [
                        "Deleting branch {name} is not allowed.".format(
                            name=self.human_readable_ref_name()
                        ),
                        "",
                        "This repository currently only allow the deletion of"
                        " references",
                        "whose name matches the following:",
                        "",
                    ]
                    + ["    {}".format(allowed) for allowed in allowed_list]
                )

            tip = git_config('hooks.rejected-branch-deletion-tip')
            if tip is None:
                tip = DEFAULT_REJECTED_BRANCH_DELETION_TIP
            err.append("")
            err.extend(tip.splitlines())

            raise InvalidUpdate(*err)

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
