"""Management of git commits during updates..."""

from git import git
from utils import debug

class CommitInfo(object):
    """A git commit.

    ATTRIBUTES
        rev: The commit's revision (SHA1).
        subject: The subject of the commit.
        pre_existing_p: True if this commit was accessible from
            any of the existing references prior to this update.
            False if it was not. None if the value has not been
            determined yet.
        base_rev: The revision (SHA1) of the commit's parent,
            for "diff'ing" purpose (determining what changes are
            introduced by this commit).
            The null revision if this is a headless commit.
            None if the value has not been determined yet.
    """
    def __init__(self, rev, subject, base_rev=None):
        self.rev = rev
        self.subject = subject
        self.pre_existing_p = None
        self.base_rev = base_rev

    def oneline_str(self):
        """A one-line string description of the commit.
        """
        return '%s... %s' % (self.rev[:7], self.subject[:59])


def commit_info_list(*args):
    """Return a list of CommitInfo objects in chronological order.

    PARAMETERS
        Same as in the "git rev-list" command.
    """
    # In the following call to "git.rev_list", we list the --oneline
    # and --no-abbrev arguments explicitly instead of using
    # the usual named arguments, because the order between named
    # arguments is not guaranteed to be preserved.  In this case,
    # the order between the oneline and no-abbrev switches
    # is very important to make sure we get non-abbreviated commit revs.
    all_revs = git.rev_list('--oneline', '--no-abbrev', *args,
                            _split_lines=True, reverse=True)

    result = []
    prev_rev = None
    for rev_info in all_revs:
        rev, subject = rev_info.split(None, 1)
        result.append(CommitInfo(rev, subject, prev_rev))
        prev_rev = rev

    return result
