"""Handling of annotated tag updates."""

from git import is_null_rev, parse_tag_object, commit_oneline
from updates.tags import (
    AbstractTagUpdate, warn_about_tag_update, tag_summary_of_changes_needed)

ATAG_UPDATE_EMAIL_BODY_TEMPLATE = """\
The %(tag_kind)s tag %(tag_name)s was updated to point to:

 %(commit_oneline)s

It previously pointed to:

 %(old_commit_oneline)s

Tagger: %(tagger)s
Date: %(date)s

%(message)s"""


class AnnotatedTagUpdate(AbstractTagUpdate):
    """Update class for annotated tag update.

    REMARKS
        The implementation of some of the abstract methods are expected
        to handle tag creation as well.  This is because creation is
        a special kind of update, and thus some of the actions required
        to handle the creation are identical to those required to handle
        a tag value change.  The methods that handle both creation and
        update are documented via their REMARKS section.
    """
    def self_sanity_check(self):
        """See AbstractUpdate.self_sanity_check."""
        assert self.new_rev_type == 'tag'

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update.

        REMARKS
            This method is capable of handling both creation update.
        """
        # Annotated tag creation/updates are always allowed.
        #
        # But, if this is a pre-existing tag being updated, there are
        # pitfalls that the user should be warned about.
        if not is_null_rev(self.old_rev) and not is_null_rev(self.new_rev):
            warn_about_tag_update(self.human_readable_tag_name(),
                                  self.old_rev, self.new_rev)

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
        subject = '[%s] Updated tag %s' % (self.email_info.project_name,
                                           self.human_readable_tag_name())

        tag_info = parse_tag_object(self.ref_name)
        # Augment tag_info with some of other elements that will be
        # provided in the mail body.  This is just to make it easier
        # to format the message body...
        tag_info['tag_kind'] = 'signed' if tag_info['signed_p'] else 'unsigned'
        tag_info['tag_name'] = self.human_readable_tag_name()
        tag_info['commit_oneline'] = commit_oneline(self.new_rev)
        tag_info['old_commit_oneline'] = commit_oneline(self.old_rev)

        body = ATAG_UPDATE_EMAIL_BODY_TEMPLATE % tag_info
        if tag_summary_of_changes_needed(self.added_commits,
                                         self.lost_commits):
            body += self.summary_of_changes()

        return (self.everyone_emails(), subject, body)
