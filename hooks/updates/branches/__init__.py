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

    # Send a summary if any of the commits was marked as "no email".
    # Since the user is not going to see the commit email for those
    # commits, it's good to send a summary email in order to have
    # have a trace of that commit.
    for commit in added_commits:
        if not commit.send_email_p:
            return True

    # The question was raised whether we should include the summary
    # if one of the commits is a merge commit.  At the moment,
    # we do not see a reason why merge commits should be treated
    # differently from other commits.

    return False
