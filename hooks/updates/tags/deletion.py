"""Handling of tag deletion."""

from config import git_config
from updates import AbstractUpdate
from utils import InvalidUpdate

class TagDeletion(AbstractUpdate):
    """Update object for tag deletion.

    REMARKS
        This class does not make a difference between annotated tags
        and lightweight tags, and treats them identically.
    """
    def self_sanity_check(self):
        """See AbstractUpdate.self_sanity_check."""
        assert self.ref_name.startswith('refs/tags/')
        assert self.new_rev_type == 'delete'

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update."""
        if git_config('hooks.allowdeletetag') != "true":
            raise InvalidUpdate(
                "Deleting a tag is not allowed in this repository")
