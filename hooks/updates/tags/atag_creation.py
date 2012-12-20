"""Handling of annotated tag creation."""

from updates.tags import tag_summary_of_changes_needed
from updates.tags.atag_update import AnnotatedTagUpdate
from git import commit_oneline, parse_tag_object

ATAG_CREATION_EMAIL_BODY_TEMPLATE = """\
The %(tag_kind)s tag '%(short_ref_name)s' was created pointing to:

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
    def get_update_email_contents(self, email_info, added_commits,
                                  lost_commits):
        """See AbstractUpdate.get_update_email_contents."""
        subject = '[%s] Created tag %s' % (email_info.project_name,
                                           self.short_ref_name)

        tag_info = parse_tag_object(self.short_ref_name)
        # Augment tag_info with some of other elements that will be
        # provided in the mail body.  This is just to make it easier
        # to format the message body...
        tag_info['tag_kind'] = 'signed' if tag_info['signed_p'] else 'unsigned'
        tag_info['short_ref_name'] = self.short_ref_name
        tag_info['commit_oneline'] = commit_oneline(self.new_rev)

        body = ATAG_CREATION_EMAIL_BODY_TEMPLATE % tag_info
        if tag_summary_of_changes_needed(added_commits, lost_commits):
            body += self.summary_of_changes(added_commits, lost_commits)

        return (subject, body)
