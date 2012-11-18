"""Handling of annotated tag updates."""

from git import is_null_rev
from updates import AbstractUpdate
from updates.tags import warn_about_tag_update

class AnnotatedTagUpdate(AbstractUpdate):
    """Update class for annotated tag creation.
    """
    def self_sanity_check(self):
        """See AbstractUpdate.self_sanity_check."""
        assert self.ref_name.startswith('refs/tags/')
        assert self.new_rev_type == 'tag'

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update."""
        # Annotated tag creation/updates are always allowed.
        #
        # But, if this is a pre-existing tag being updated, there are
        # pitfalls that the user should be warned about.
        if not is_null_rev(self.old_rev) and not is_null_rev(self.new_rev):
            warn_about_tag_update(self.short_ref_name,
                                  self.old_rev, self.new_rev)

