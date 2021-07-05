"""Implements git's pre-receive hook.

The arguments for this hook are passed via stdin: For each reference
being sent for update, stdin contains one line with that reference's
name (Eg: refs/heads/master).
"""
from collections import OrderedDict
import sys

from config import CONFIG_REF, ThirdPartyHook
from errors import InvalidUpdate
from git import is_null_rev
from init import init_all_globals
from utils import warn


def pre_receive(refs_data):
    """Implement the pre-receive hook.

    PARAMETERS
        refs_data: An OrderedDict, indexed by the name of the ref
            being updated, and containing 2-elements tuple.  This tuple
            contains the previous revision, and the new revision of the
            reference.
    """
    # Enforce a rule that, if the CONFIG_REF reference is being updated,
    # then it must be the only reference being updated.
    #
    # Rationale:
    # ----------
    #
    # The CONFIG_REF reference has special significance for us, as
    # this is the reference where we load the repository's configuration
    # from. And when a user pushes an update to that reference, it really
    # makes better sense to immediately take the changes it brings into
    # account. For instance, if we realized that the hooks are configured
    # with the wrong mailing-list address, and we push a change to fix
    # that, we want the corresponding email to be sent to the correct
    # address. Similarly, it allows us, during the initial repository
    # setup phase, to enable the hooks prior to adding the hooks's config,
    # followed by pushing the initial config as usual, so as to get
    # the benefits of having the hooks perform the necessary validation
    # checks and send emails when relevant.
    #
    # Now, the reason why we need to enforce that CONFIG_REF updates
    # be done on their own is because the update hook gets called
    # once per reference being updated. What this means is that
    # the update script doesn't have enough context to determine
    # with certainty where to get the correct configuration from.
    # Enforcing CONFIG_REF updates to be done on their own push
    # solves that problem.
    if len(refs_data) > 1 and CONFIG_REF in refs_data:
        err_msg = ["You are trying to push multiple references at the same time:"]
        err_msg.extend("  - {}".format(ref_name) for ref_name in sorted(refs_data))
        err_msg.extend(
            [
                "",
                "Updates to the {CONFIG_REF} reference must be pushed".format(
                    CONFIG_REF=CONFIG_REF
                ),
                "on their own. Please push this reference first, and then",
                "retry pushing the remaining references.",
            ]
        )
        raise InvalidUpdate(*err_msg)

    # Verify that we are not trying to delete the CONFIG_REF reference.
    # This is not allowed, because this would delete the repository's
    # configuration. We do this extra early so as to provide the user
    # with a clear message rather than hitting an error later on, when
    # we may not have enough context to generate a clear error message.
    if CONFIG_REF in refs_data:
        _, new_rev = refs_data[CONFIG_REF]
        if is_null_rev(new_rev):
            raise InvalidUpdate(
                "Deleting the reference {CONFIG_REF} is not allowed.".format(
                    CONFIG_REF=CONFIG_REF
                ),
                "",
                "This reference provides important configuration information",
                "and thus must not be deleted.",
            )


def maybe_pre_receive_hook(pre_receive_data):
    """Call the pre-receive-hook if defined.

    This function implements supports for the hooks.pre-receive-hook
    config variable, by calling this function if the config variable
    is defined.

    ARGUMENTS
        pre_receive_data: The data received via stdin by the pre-receive hook.
    """
    result = ThirdPartyHook("hooks.pre-receive-hook").call_if_defined(
        hook_input=pre_receive_data
    )
    if result is not None:
        hook_exe, p, out = result
        if p.returncode != 0:
            raise InvalidUpdate(
                "Update rejected by this repository's hooks.pre-receive-hook" " script",
                "({}):".format(hook_exe),
                *out.splitlines()
            )
        else:
            sys.stdout.write(out)


if __name__ == "__main__":
    stdin = sys.stdin.read()
    refs_data = OrderedDict()
    for line in stdin.splitlines():
        old_rev, new_rev, ref_name = line.strip().split()
        refs_data[ref_name] = (old_rev, new_rev)

    try:
        init_all_globals(refs_data)
        pre_receive(refs_data)
        maybe_pre_receive_hook(stdin)
    except InvalidUpdate as e:
        # The update was rejected.  Print the rejection reason, and
        # exit with a nonzero status.
        warn(*e.args)
        sys.exit(1)
