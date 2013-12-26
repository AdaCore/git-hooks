"""Handling of Git Notes creation."""

from updates.notes.update import NotesUpdate


class NotesCreation(NotesUpdate):
    """Update object for Git Notes creation."""
    # Notes creation is a special case of Notes Update, where the
    # old_rev is the null revision.  The NotesUpdate class currently
    # handles everything correctly for us, so no extra code needed.
    pass
