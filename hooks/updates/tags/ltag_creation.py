"""Handling of lightweight tag creation."""

from updates.tags import tag_summary_of_changes_needed
from updates.tags.ltag_update import LightweightTagUpdate
from git import commit_oneline

LTAG_CREATION_EMAIL_BODY_TEMPLATE = """\
The lightweight tag %(tag_name)s was created pointing to:

 %(commit_oneline)s"""


class LightweightTagCreation(LightweightTagUpdate):
    """Update class for lightweight tag creation.

    REMARKS
        Creation is a special case of update, and the implementation of
        some of the abstract methods would be identical.  So inherit
        from LightweightTagUpdate.
    """
    def get_update_email_contents(self):
        """See AbstractUpdate.get_update_email_contents."""
        subject = '[%s] Created tag %s' % (self.email_info.project_name,
                                           self.human_readable_tag_name())

        body = (LTAG_CREATION_EMAIL_BODY_TEMPLATE
                % {'tag_name': self.human_readable_tag_name(),
                   'commit_oneline': commit_oneline(self.new_rev),
                   })
        if tag_summary_of_changes_needed(self.added_commits,
                                         self.lost_commits):
            body += self.summary_of_changes()

        return (self.everyone_emails(), subject, body)
