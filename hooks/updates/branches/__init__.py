"""Branch updates root module."""


def branch_summary_of_changes_needed(added_commits, lost_commits):
    """Return True iff the summary of changes is needed...

    Assuming a branch update  (in the general sense, meaning either
    a creation, deletion or reference change), inspect the list
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

    # If this update introduces some pre-existing commits (for
    # which individual emails are not going to be sent), send
    # the summary as well.
    for commit in added_commits:
        if commit.pre_existing_p:
            return True

    # The question was raised whether we should include the summary
    # if one of the commits is a merge commit.  At the moment,
    # we do not see a reason why merge commits should be treated
    # differently from other commits.

    return False
