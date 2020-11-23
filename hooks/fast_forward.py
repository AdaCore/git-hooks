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
from git import git
from utils import warn

# A list of regular expressions that match the references where
# it will always be OK to do a non-fast-forward update (aka
# a "forced update").
FORCED_UPDATE_OK_REFS = ("refs/heads/topic/.*",)

# The error message shown to the user when rejecting a non-fast-forward
# update.
NON_FAST_FORWARD_ERROR_MESSAGE = """\
Non-fast-forward updates are not allowed for this reference.
Please rebase your changes on top of the latest HEAD,
and then try pushing again."""

# A warning added at the end of the NON_FAST_FORWARD_ERROR_MESSAGE
# when we believe the user is trying to push a non-fast-forward update
# to a branch that looks like it should be allowed, and yet isn't,
# because this repository's hooks.non-fast-forward configuration
# appears to be following the previous (now defunct) semantics.

OLD_STYLE_CONFIG_WARNING = """\
Note: It looks like the hooks.non-fast-forward configuration
for your repository is set to only match the name of the branch
being updated (e.g. "master"), which is how this configuration
option was originally interpreted. However, the semantics of
this option has since been changed and its values must now match
the reference name (e.g. "refs/heads/master"). If you believe
this non-fast-forward update should be allowed on this branch,
contact your repository adminstrator to review the repository's
hooks.non-fast-forward option configuration."""


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

    # Non-fast-forward update.  See if this is one of the references
    # where such an update is allowed.
    ok_refs = git_config('hooks.allow-non-fast-forward')

    for ok_ref_re in ok_refs + FORCED_UPDATE_OK_REFS:
        if re.match(ok_ref_re, ref_name) is not None:
            # This is one of the branches where a non-fast-forward update
            # is allowed.  Allow the update, but print a warning for
            # the user, just to make sure he is completely aware of
            # the changes that just took place.
            warn("!!! WARNING: This is *NOT* a fast-forward update.")
            warn("!!! WARNING: You may have removed some important commits.")
            return

    # This non-fast-forward update is not allowed.
    err_msg = NON_FAST_FORWARD_ERROR_MESSAGE

    # In the previous version of these hooks, the allow-non-fast-forward
    # config was assuming that all such updates would be on references
    # whose name starts with 'refs/heads/'. This is no longer the case.
    # For repositories using this configuration option with the old
    # semantics, non-fast-forward updates will now start getting rejected.
    #
    # To help users facing this situation understand what's going on,
    # see if this non-fast-forward update would have been accepted
    # when interpreting the config option the old way; if yes, then
    # we are probably in a situation where it's the config rather than
    # the update that's a problem. Add some additional information
    # to the error message in order to help him understand what's
    # is likely happening.
    if ref_name.startswith('refs/heads/'):
        for ok_ref_re in ['refs/heads/' + branch.strip()
                          for branch in ok_refs]:
            if re.match(ok_ref_re, ref_name) is not None:
                err_msg += '\n\n' + OLD_STYLE_CONFIG_WARNING
                break

    raise InvalidUpdate(*err_msg.splitlines())


if __name__ == '__main__':
    # First, retrieve the command-line arguments.
    if len(sys.argv) != 4:
        warn("Error(%s): Invalid usage, wrong number of arguments (%d)"
             % (sys.argv[0], len(sys.argv)))
        sys.exit(1)
    try:
        check_fast_forward(sys.argv[1], sys.argv[2], sys.argv[3])
    except InvalidUpdate as E:
        # The update was rejected.  Print the rejection reason, and
        # exit with a nonzero status.
        warn(*E)
        sys.exit(1)
