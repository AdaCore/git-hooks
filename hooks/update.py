from argparse import ArgumentParser
from shutil import rmtree
import sys

from git import get_object_type
from utils import (InvalidUpdate, debug, warn, create_scratch_dir)
# We have to import utils, because we cannot import scratch_dir
# directly into this module.  Otherwise, our scratch_dir seems
# to not see the update when create_scratch_dir is called.
import utils

from updates.factory import new_update

def parse_command_line():
    """Return a namespace built after parsing the command line.
    """
    # The command-line interface is very simple, so we could possibly
    # handle it by hand.  But it's nice to have features such as
    # -h/--help switches which come for free if we use argparse.
    #
    # We use ArgumentParser, which means that we are requiring
    # Python version 2.7 or later, because it handles mandatory
    # command-line arguments for us as well.
    ap = ArgumentParser(description='Git "update" hook.')
    ap.add_argument('ref_name',
                    help='the name of the reference being updated')
    ap.add_argument('old_rev',
                    help='the SHA1 before update')
    ap.add_argument('new_rev',
                    help='the new SHA1, if the update is accepted')
    return ap.parse_args()


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
    debug('check_update(ref_name=%s, old_rev=%s, new_rev=%s)'
          % (ref_name, old_rev, new_rev),
          level=2)
    update_cls = new_update(ref_name, old_rev, new_rev)
    if update_cls is None:
        raise InvalidUpdate(
            "This type of update (%s,%s) is currently unsupported."
            % (ref_name, get_object_type(new_rev)))
    update_cls.validate()


if __name__ == "__main__":
    args = parse_command_line()
    try:
        create_scratch_dir()
        check_update(args.ref_name, args.old_rev, args.new_rev)
    except InvalidUpdate, E:
        # The update was rejected.  Print the rejection reason, and
        # exit with a nonzero status.
        warn(*E)
        sys.exit(1)
    finally:
        # Delete our scratch directory.
        if utils.scratch_dir is not None:
            rmtree(utils.scratch_dir)


