from argparse import ArgumentParser
import re
import sys

from config import git_config
from git import git
from utils import InvalidUpdate, debug, warn


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


def get_object_type(rev):
    """Determine the object type of the given commit.

    PARAMETERS
        rev: The commit SHA1 that we want to inspect.

    RETURN VALUE
        The string returned by "git cat-file -t REV", or else "delete"
        if REV is a null SHA1 (all zeroes).
    """
    if re.match("0+", rev):
        rev_type = "delete"
    else:
        rev_type = git.cat_file(rev, t=True)
    return rev_type


def check_unannotated_tag(ref_name, old_rev, new_rev):
    """Do the check_update work for a new un-annotated tag.
    """
    debug('check_unannotated_tag (%s)' % ref_name)

    if git_config('hooks.allowunannotated') == "true":
        return

    # Update not permitted, raise InvalidUpdate.
    assert ref_name.startswith('refs/tags/')
    tag_name = ref_name[len('refs/tags/'):]
    raise InvalidUpdate(
        "Un-annotated tags (%s) are not allowed in this repository." % tag_name,
        "Use 'git tag [ -a | -s ]' for tags you want to propagate.")


def check_tag_deletion(ref_name, old_rev, new_rev):
    """Do the check_update work for a tag deletion.
    """
    debug('check_tag_deletion(%s)' % ref_name)

    if git_config('hooks.allowdeletetag') == "true":
        return

    # Update not permitted, raise InvalidUpdate.
    assert ref_name.startswith('refs/tags/')
    tag_name = ref_name[len('refs/tags/'):]
    raise InvalidUpdate("Deleting a tag is not allowed in this repository")


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
    """
    new_rev_type = get_object_type(new_rev)
    if ref_name.startswith('refs/tags/') and new_rev_type == 'commit':
        check_unannotated_tag(ref_name, old_rev, new_rev)
    elif ref_name.startswith('refs/tags/') and new_rev_type == 'delete':
        check_tag_deletion(ref_name, old_rev, new_rev)
    else:
        raise InvalidUpdate(
            "This type of update (%s,%s) is currently unsupported."
            % (ref_name, new_rev_type))


if __name__ == "__main__":
    args = parse_command_line()
    try:
        check_update(args.ref_name, args.old_rev, args.new_rev)
    except InvalidUpdate, E:
        # The update was rejected.  Print the rejection reason, and
        # exit with a nonzero status.
        warn(*E)
        sys.exit(1)


