"""Handling of annotated tag creation."""

from updates.tags.atag_update import AnnotatedTagUpdate

class AnnotatedTagCreation(AnnotatedTagUpdate):
    """Update class for annotated tag creation.

    REMARKS
        Creation is a special case of update, and the implementation of
        some of the abstract methods would be identical.  So inherit
        from AnnotatedTagUpdate.
    """
    # For now, nothing different.
    pass
