"""Handling of lightweight tag deletion."""

from config import git_config
from errors import InvalidUpdate
from git import commit_oneline
from updates import AbstractUpdate
from updates.tags import tag_summary_of_changes_needed

LTAG_DELETION_EMAIL_BODY_TEMPLATE = """\
The lightweight tag '%(short_ref_name)s' was deleted.
It previously pointed to:

 %(commit_oneline)s"""


class LightweightTagDeletion(AbstractUpdate):
    """Update object for lightweight tag deletion.

    REMARKS
        For tag deletion, there are only very small differences
        between lightweight tags and annotated tags.  Therefore,
        the implementation of some of the abstract methods is
        identical for both, and we expect the class handling
        annotated tags to inherit from us.  Methods that handle
        both annotated and lightweight tags, and thus should be
        inherited, are clearly documented as such in their REMARKS
        section.
    """
    def self_sanity_check(self):
        """See AbstractUpdate.self_sanity_check.

        REMARKS
            This method handles both lightweight and annotated tags.
        """
        assert self.ref_name.startswith('refs/tags/')
        assert self.new_rev_type == 'delete'

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update.

        REMARKS
            This method handles both lightweight and annotated tags.
        """
        if git_config('hooks.allow-delete-tag') != "true":
            raise InvalidUpdate(
                "Deleting a tag is not allowed in this repository")

    def get_update_email_contents(self, email_info):
        """See AbstractUpdate.get_update_email_contents."""
        subject = '[%s] Deleted tag %s' % (email_info.project_name,
                                           self.short_ref_name)

        body = (LTAG_DELETION_EMAIL_BODY_TEMPLATE
                % {'short_ref_name' : self.short_ref_name,
                   'commit_oneline' : commit_oneline(self.old_rev),
                  })
        if tag_summary_of_changes_needed(self.added_commits,
                                         self.lost_commits):
            body += self.summary_of_changes()

        return (subject, body)
