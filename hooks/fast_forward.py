#! /usr/bin/env python
"""A module to handle the fast-forward policies...

This module can also be called as a script, and returns non-zero if
it detects that a non-fast-forward update being attempted on a branch
where it is not allowed. When such an error is detected, an informative
error message should be printed on stderr.

Usage: fast_forward.py REF_NAME OLD_REV NEW_REV

    The arguments REF_NAME, OLD_REV and NEW_REV are identical
    to the arguments used when git calls the "update" hook.

"""

import re
import sys

from config import git_config
from errors import InvalidUpdate
from git import *
from utils import warn

# A list of regular expressions that match the branches where
# it will always be OK to do a non-fast-forward update (aka
# a "forced update").
FORCED_UPDATE_OK_BRANCHES = ("topic/.*",)


def check_fast_forward(ref_name, old_rev, new_rev):
    """Raise InvalidUpdate if the update violates the fast-forward policy.

    PARAMETERS
        ref_name: The name of the reference being update (Eg:
            refs/heads/master).
        old_rev: The commit SHA1 of the reference before the update.
        new_rev: The new commit SHA1 that the reference will point to
            if the update is accepted.
    """
    # Non-fast-foward updates can be characterized by the fact that
    # there is at least one commit that is accessible from the old
    # revision which would no longer be accessible from the new revision.
    if git.rev_list("%s..%s" % (new_rev, old_rev)) == "":
        # This is a fast-forward update.
        return

    # Non-fast-forward update.  See if this is one of the branches where
    # such an update is allowed.
    ok_branches = git_config('hooks.allow-non-fast-forward')

    for branch in ["refs/heads/" + branch.strip()
                   for branch in ok_branches + FORCED_UPDATE_OK_BRANCHES]:
        if re.match(branch, ref_name) is not None:
            # This is one of the branches where a non-fast-forward update
            # is allowed.  Allow the update, but print a warning for
            # the user, just to make sure he is completely aware of
            # the changes that just took place.
            warn("!!! WARNING: This is *NOT* a fast-forward update.")
            warn("!!! WARNING: You may have removed some important commits.")
            return

    # This non-fast-forward update is not allowed.
    raise InvalidUpdate(
        'Non-fast-forward updates are not allowed on this branch;',
        'Please rebase your changes on top of the latest HEAD,',
        'and then try pushing again.')


if __name__ == '__main__':
    # First, retrieve the command-line arguments.
    if len(sys.argv) != 4:
        warn("Error(%s): Invalid usage, wrong number of arguments (%d)"
             % (sys.argv[0], len(sys.argv)))
        sys.exit(1)
    try:
        check_fast_forward(sys.argv[1], sys.argv[2], sys.argv[3])
    except InvalidUpdate, E:
        # The update was rejected.  Print the rejection reason, and
        # exit with a nonzero status.
        warn(*E)
        sys.exit(1)
