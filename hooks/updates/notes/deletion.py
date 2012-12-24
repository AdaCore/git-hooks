"""Handling of Git Notes deletion."""

from updates import AbstractUpdate
from utils import InvalidUpdate

class NotesDeletion(AbstractUpdate):
    """Update object for Git Notes deletion."""
    def self_sanity_check(self):
        """See AbstractUpdate.self_sanity_check."""
        assert self.ref_name == 'refs/notes/commits'

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update."""
        # Deleting the Git Notes branch is never allowed.
        raise InvalidUpdate('Deleting the Git Notes is not allowed.')
