"""Handling of unannotated tag updates."""

from config import git_config
from git import is_null_rev
from updates import AbstractUpdate
from updates.tags import warn_about_tag_update
from utils import InvalidUpdate

class UnannotatedTagUpdate(AbstractUpdate):
    """Update class for unannotated tag creation.
    """
    def self_sanity_check(self):
        """See AbstractUpdate.self_sanity_check."""
        assert self.ref_name.startswith('refs/tags/')
        assert self.new_rev_type == 'commit'

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update."""
        # If lightweight tags are not allowed, refuse the update.
        if git_config('hooks.allowunannotated') != "true":
            raise InvalidUpdate(
                "Un-annotated tags (%s) are not allowed in this repository."
                    % self.short_ref_name,
                "Use 'git tag [ -a | -s ]' for tags you want to propagate.")

        # If this is a pre-existing tag being updated, there are pitfalls
        # that the user should be warned about.
        if not is_null_rev(self.old_rev) and not is_null_rev(self.new_rev):
            warn_about_tag_update(self.short_ref_name,
                                  self.old_rev, self.new_rev)
