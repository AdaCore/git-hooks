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


def tag_summary_of_changes_needed(added_commits, lost_commits):
    """Return True iff the summary of changes is needed...

    Assuming a tag update  (in the general sense, meaning either
    a creation, deletion or refernce change), inspect the list
    of added and lost commits, and return True iff the update
    email should include a summary of changes.

    PARAMETERS
        added_commits: A list of CommitInfo objects, corresponding to
            the commits added by this update.
        lost_commits: A list of CommitInfo objects, corresponding to
            the commits lost after this update.
    """
    # If some commits are no longer accessible from the new
    # revision, definitely send the summary.
    if lost_commits:
        return True

    # For new tags (creation), we usually expect them to point
    # to pre-existing commit, which means that added_commits
    # should be empty.  We should therefore generate a summary
    # of changes if that's not the case.
    #
    # For tag updates, it seems like a good idea to document
    # in the update email which commits are now accessible
    # from the new tag value.  This means generating a summary
    # of changes when added_commits is not empty.
    #
    # Regardless of the situation, it does not matter whether
    # the commits might be pre-existing or not.
    if added_commits:
        return True

    return False
