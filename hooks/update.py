from argparse import ArgumentParser
from shutil import rmtree
import sys

from git import get_object_type
from utils import (InvalidUpdate, debug, warn, scratch_dir,
                   create_scratch_dir)

from updates.tags.atag_update import AnnotatedTagUpdate
from updates.tags.utag_update import LightweightTagUpdate
from updates.tags.deletion import TagDeletion
from updates.branches.update import BranchUpdate

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
    new_rev_type = get_object_type(new_rev)
    if ref_name.startswith('refs/heads/') and new_rev_type == 'commit':
        BranchUpdate(ref_name, old_rev, new_rev).validate()
    elif ref_name.startswith('refs/tags/') and new_rev_type == 'tag':
        AnnotatedTagUpdate(ref_name, old_rev, new_rev).validate()
    elif ref_name.startswith('refs/tags/') and new_rev_type == 'commit':
        LightweightTagUpdate(ref_name, old_rev, new_rev).validate()
    elif ref_name.startswith('refs/tags/') and new_rev_type == 'delete':
        TagDeletion(ref_name, old_rev, new_rev).validate()
    else: # pragma: no cover (should be impossible)
        raise InvalidUpdate(
            "This type of update (%s,%s) is currently unsupported."
            % (ref_name, new_rev_type))


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
        if scratch_dir is not None:
            rmtree(scratch_dir)


