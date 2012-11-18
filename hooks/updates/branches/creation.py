"""Handling of branch creation."""

from updates.branches.update import BranchUpdate

class BranchCreation(BranchUpdate):
    """Update class for branch creation.

    REMARKS
        Creation is a special case of update, and the implementation of
        some of the abstract methods would be identical.  So inherit
        from BranchUpdate.
    """
    # For now, nothing different.
    pass
