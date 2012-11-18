"""Handling of annotated tag deletion."""

from updates.tags.ltag_deletion import LightweightTagDeletion

class AnnotatedTagDeletion(LightweightTagDeletion):
    """Update class for annotated tag deletion.

    REMARKS
        For tag deletion, there are only very small differences
        between lightweight tags and annotated tags.  Therefore,
        the implementation of some of the abstract methods is
        identical for both.  This explains why we inherit from
        LightweightTagDeletion.
    """
    # Nothing new for now.
    pass
