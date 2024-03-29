"""Handling of lightweight tag updates."""

from config import git_config
from errors import InvalidUpdate
from git import is_null_rev, commit_oneline
from updates import RefKind
from updates.tags import (
    AbstractTagUpdate,
    warn_about_tag_update,
    tag_summary_of_changes_needed,
)

LTAG_UPDATE_EMAIL_BODY_TEMPLATE = """\
The lightweight tag %(tag_name)s was updated to point to:

 %(commit_oneline)s

It previously pointed to:

 %(old_commit_oneline)s"""


class LightweightTagUpdate(AbstractTagUpdate):
    """Update class for Lightweight tag update.

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
        assert self.ref_kind == RefKind.tag_ref and self.object_type == "commit"

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update.

        REMARKS
            This method is capable of handling both creation update.
        """
        # If lightweight tags are not allowed, refuse the update.
        if not git_config("hooks.allow-lightweight-tag"):
            raise InvalidUpdate(
                "Lightweight tags (%s) are not allowed in this repository."
                % self.human_readable_tag_name(),
                "Use 'git tag [ -a | -s ]' for tags you want to propagate.",
            )

        # If this is a pre-existing tag being updated, there are pitfalls
        # that the user should be warned about.
        if not is_null_rev(self.old_rev) and not is_null_rev(self.new_rev):
            warn_about_tag_update(
                self.human_readable_tag_name(), self.old_rev, self.new_rev
            )

    def get_update_email_contents(self):
        """See AbstractUpdate.get_update_email_contents."""
        subject = "[%s] Updated tag %s" % (
            self.email_info.project_name,
            self.human_readable_tag_name(),
        )

        body = LTAG_UPDATE_EMAIL_BODY_TEMPLATE % {
            "tag_name": self.human_readable_tag_name(),
            "commit_oneline": commit_oneline(self.new_rev),
            "old_commit_oneline": commit_oneline(self.old_rev),
        }
        if tag_summary_of_changes_needed(self.new_commits_for_ref, self.lost_commits):
            body += self.summary_of_changes()

        return (self.everyone_emails(), subject, body)
