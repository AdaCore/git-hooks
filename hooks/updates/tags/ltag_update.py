"""Handling of lightweight tag updates."""

from config import git_config
from git import is_null_rev
from updates import AbstractUpdate
from updates.tags import warn_about_tag_update
from utils import InvalidUpdate

class LightweightTagUpdate(AbstractUpdate):
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
        assert self.ref_name.startswith('refs/tags/')
        assert self.new_rev_type == 'commit'

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update.

        REMARKS
            This method is capable of handling both creation update.
        """
        # If lightweight tags are not allowed, refuse the update.
        if git_config('hooks.allowlightweighttag') != "true":
            raise InvalidUpdate(
                "Lightweight tags (%s) are not allowed in this repository."
                    % self.short_ref_name,
                "Use 'git tag [ -a | -s ]' for tags you want to propagate.")

        # If this is a pre-existing tag being updated, there are pitfalls
        # that the user should be warned about.
        if not is_null_rev(self.old_rev) and not is_null_rev(self.new_rev):
            warn_about_tag_update(self.short_ref_name,
                                  self.old_rev, self.new_rev)
