from argparse import ArgumentParser
from collections import OrderedDict
from shutil import rmtree
import sys

from config import ThirdPartyHook
from errors import InvalidUpdate
from git import get_object_type, git_show_ref
from init import init_all_globals
from utils import debug, warn, create_scratch_dir, FileLock

# We have to import utils, because we cannot import scratch_dir
# directly into this module.  Otherwise, our scratch_dir seems
# to not see the update when create_scratch_dir is called.
import utils

from updates.factory import new_update


def parse_command_line():
    """Return a namespace built after parsing the command line."""
    # The command-line interface is very simple, so we could possibly
    # handle it by hand.  But it's nice to have features such as
    # -h/--help switches which come for free if we use argparse.
    #
    # We use ArgumentParser, which means that we are requiring
    # Python version 2.7 or later, because it handles mandatory
    # command-line arguments for us as well.
    ap = ArgumentParser(description='Git "update" hook.')
    ap.add_argument("ref_name", help="the name of the reference being updated")
    ap.add_argument("old_rev", help="the SHA1 before update")
    ap.add_argument("new_rev", help="the new SHA1, if the update is accepted")
    return ap.parse_args()


def maybe_update_hook(ref_name, old_rev, new_rev):
    """Call the update-hook if set in the repository's configuration.

    Raises InvalidUpdate if the hook returned nonzero, indicating
    that the update should be rejected.

    PARAMETERS
        ref_name: The name of the reference being update (Eg:
            refs/heads/master).
        old_rev: The commit SHA1 of the reference before the update.
        new_rev: The new commit SHA1 that the reference will point to
            if the update is accepted.
    """
    result = ThirdPartyHook("hooks.update-hook").call_if_defined(
        hook_args=(ref_name, old_rev, new_rev)
    )
    if result is not None:
        hook_exe, p, out = result
        if p.returncode != 0:
            raise InvalidUpdate(
                "Update rejected by this repository's hooks.update-hook" " script",
                "({}):".format(hook_exe),
                *out.splitlines()
            )
        else:
            sys.stdout.write(out)


def check_update(ref_name, old_rev, new_rev):
    """General handler of the given update.

    Raises InvalidUpdate if the update cannot be accepted (usually
    because one of the commits fails a style-check, for instance).

    PARAMETERS
        ref_name: The name of the reference being update (Eg:
            refs/heads/master).
        old_rev: The commit SHA1 of the reference before the update.
        new_rev: The new commit SHA1 that the reference will point to
            if the update is accepted.

    REMARKS
        This function assumes that scratch_dir has been initialized.
    """
    debug(
        "check_update(ref_name=%s, old_rev=%s, new_rev=%s)"
        % (ref_name, old_rev, new_rev),
        level=2,
    )
    update_cls = new_update(
        ref_name, old_rev, new_rev, git_show_ref(), submitter_email=None
    )
    if update_cls is None:
        # Report an error. We could look more precisely into what
        # might be the reason behind this error, and print more precise
        # diagnostics, but it does not seem like this would be worth
        # the effort: It requires some pretty far-fetched scenarios
        # for this to trigger; so, this should happen only very seldomly,
        # and when a user does something very unusual.
        raise InvalidUpdate(
            "This type of update (%s,%s) is not valid."
            % (ref_name, get_object_type(new_rev))
        )
    with FileLock("git-hooks::update.token"):
        update_cls.validate()
        maybe_update_hook(ref_name, old_rev, new_rev)


if __name__ == "__main__":
    args = parse_command_line()
    try:
        init_all_globals(OrderedDict([(args.ref_name, (args.old_rev, args.new_rev))]))
        create_scratch_dir()
        check_update(args.ref_name, args.old_rev, args.new_rev)
    except InvalidUpdate as E:
        # The update was rejected.  Print the rejection reason, and
        # exit with a nonzero status.
        warn(*E.args)
        sys.exit(1)
    finally:
        # Delete our scratch directory.
        if utils.scratch_dir is not None:
            rmtree(utils.scratch_dir)
