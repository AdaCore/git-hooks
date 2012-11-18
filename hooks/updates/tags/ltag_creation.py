"""Handling of lightweight tag creation."""

from updates.tags.ltag_update import LightweightTagUpdate

class LightweightTagCreation(LightweightTagUpdate):
    """Update class for lightweight tag creation.

    REMARKS
        Creation is a special case of update, and the implementation of
        some of the abstract methods would be identical.  So inherit
        from LightweightTagUpdate.
    """
    # For now, nothing different.
    pass

