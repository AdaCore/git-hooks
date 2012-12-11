"""Handling of annotated tag updates."""

from git import is_null_rev, parse_tag_object, commit_oneline
from updates import AbstractUpdate
from updates.tags import warn_about_tag_update

ATAG_UPDATE_EMAIL_BODY_TEMPLATE = """\
The %(tag_kind)s tag '%(short_ref_name)s' was updated to point to:

 %(commit_oneline)s

It previously pointed to:

 %(old_commit_oneline)s

Tagger: %(tagger)s
Date: %(date)s

%(message)s"""


class AnnotatedTagUpdate(AbstractUpdate):
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
        assert self.ref_name.startswith('refs/tags/')
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
            warn_about_tag_update(self.short_ref_name,
                                  self.old_rev, self.new_rev)

    def get_update_email_contents(self, email_info, commit_list):
        """See AbstractUpdate.get_update_email_contents."""
        subject = '[%s] Updated tag %s' % (email_info.project_name,
                                           self.short_ref_name)

        tag_info = parse_tag_object(self.short_ref_name)
        # Augment tag_info with some of other elements that will be
        # provided in the mail body.  This is just to make it easier
        # to format the message body...
        tag_info['tag_kind'] = 'signed' if tag_info['signed_p'] else 'unsigned'
        tag_info['short_ref_name'] = self.short_ref_name
        tag_info['commit_oneline'] = commit_oneline(self.new_rev)
        tag_info['old_commit_oneline'] = commit_oneline(self.old_rev)

        body = ATAG_UPDATE_EMAIL_BODY_TEMPLATE % tag_info

        return (subject, body)
