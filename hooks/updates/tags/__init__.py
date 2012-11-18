"""tags root module."""

from utils import warn

def warn_about_tag_update(tag_name, old_rev, new_rev):
    """Emit a warning about tag updates.

    PARAMETER
        tag_name: The name of the tag being updated.
        old_rev: The old revision referenced by the tag.
        new_rev: The new revision referenced by the tag.
    """
    warn('---------------------------------------------------------------',
         '--  IMPORTANT NOTICE:',
         '--',
         '--  You just updated the "%s" tag as follow:' % tag_name,
         '--    old SHA1: %s' % old_rev,
         '--    new SHA1: %s' % new_rev,
         '--',
         '-- Other developers pulling from this repository will not',
         '-- get the new tag. Assuming this update was deliberate,',
         '-- notifying all known users of the update is recommended.',
         '---------------------------------------------------------------')
