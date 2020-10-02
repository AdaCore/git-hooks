"""Handling of annotated tag creation."""

from updates.tags import tag_summary_of_changes_needed
from updates.tags.atag_update import AnnotatedTagUpdate
from git import commit_oneline, parse_tag_object

ATAG_CREATION_EMAIL_BODY_TEMPLATE = """\
The %(tag_kind)s tag %(tag_name)s was created pointing to:

 %(commit_oneline)s

Tagger: %(tagger)s
Date: %(date)s

%(message)s"""


class AnnotatedTagCreation(AnnotatedTagUpdate):
    """Update class for annotated tag creation.

    REMARKS
        Creation is a special case of update, and the implementation of
        some of the abstract methods would be identical.  So inherit
        from AnnotatedTagUpdate.
    """
    @property
    def send_cover_email_to_filer(self):
        """See AbstractUpdate.send_cover_email_to_filer.

        For annotated tags, we want to file the cover email, because
        the email contains a message which may include one or more TNs.
        We want that message filed, as no other email is going to
        contain that information.
        """
        return True

    def get_update_email_contents(self):
        """See AbstractUpdate.get_update_email_contents."""
        subject = '[%s] Created tag %s' % (self.email_info.project_name,
                                           self.human_readable_tag_name())

        tag_info = parse_tag_object(self.ref_name)
        # Augment tag_info with some of other elements that will be
        # provided in the mail body.  This is just to make it easier
        # to format the message body...
        tag_info['tag_kind'] = 'signed' if tag_info['signed_p'] else 'unsigned'
        tag_info['tag_name'] = self.human_readable_tag_name()
        tag_info['commit_oneline'] = commit_oneline(self.new_rev)

        body = ATAG_CREATION_EMAIL_BODY_TEMPLATE % tag_info
        if tag_summary_of_changes_needed(self.new_commits_for_ref,
                                         self.lost_commits):
            body += self.summary_of_changes()

        return (self.everyone_emails(), subject, body)
