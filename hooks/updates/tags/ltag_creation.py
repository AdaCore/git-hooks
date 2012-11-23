"""Handling of lightweight tag creation."""

from updates.tags.ltag_update import LightweightTagUpdate
from git import commit_oneline

LTAG_CREATION_EMAIL_BODY_TEMPLATE = """\
The lightweight tag '%(short_ref_name)s' was created pointing to:

 %(commit_oneline)s"""


class LightweightTagCreation(LightweightTagUpdate):
    """Update class for lightweight tag creation.

    REMARKS
        Creation is a special case of update, and the implementation of
        some of the abstract methods would be identical.  So inherit
        from LightweightTagUpdate.
    """
    def get_update_email_contents(self, email_info):
        """See AbstractUpdate.get_update_email_contents."""
        subject = '[%s] Created tag %s' % (email_info.project_name,
                                           self.short_ref_name)

        body = (LTAG_CREATION_EMAIL_BODY_TEMPLATE
                % {'short_ref_name' : self.short_ref_name,
                   'commit_oneline' : commit_oneline(self.new_rev),
                  })

        return (subject, body)
