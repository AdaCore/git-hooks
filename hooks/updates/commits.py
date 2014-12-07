"""Management of git commits during updates..."""

from git import git
from config import git_config


class CommitInfo(object):
    """A git commit.

    ATTRIBUTES
        rev: The commit's revision (SHA1).
        author: The author of the commit.
        subject: The subject of the commit.
        base_rev: The revision (SHA1) of the commit's parent,
            for "diff'ing" purpose (determining what changes are
            introduced by this commit).
            The null revision if this is a headless commit.
            None if the value has not been determined yet.
        pre_existing_p: True if this commit already existed in another
            branch prior to the update, False otherwise. May be None,
            meaning that the value of that attribute has not been
            computed yet.
        send_email_p: True if a commit email should be sent for
            this commit, False otherwise. May be None, meaning that
            the value of that attribute has not been computed yet.
        email_to: A list of email addresses, in RFC 822 format, of
            the recipients of the email notification for this commit.
    """
    def __init__(self, rev, author, subject, base_rev=None):
        self.rev = rev
        self.author = author
        self.subject = subject
        self.base_rev = base_rev
        self.pre_existing_p = None
        self.send_email_p = None

        # Implement the "email_to" attribute as a property to allow
        # us to compute it only when needed.  Once computed, we store
        # its value in self.__email_to.
        self.__email_to = None

    def oneline_str(self):
        """A one-line string description of the commit.
        """
        return '%s... %s' % (self.rev[:7], self.subject[:59])

    @property
    def email_to(self):
        """Return the email_to attribute.

        Implemented as a property in order for its initialization
        to be performed only when required.
        """
        if self.__email_to is None:
            self.__email_to = git_config('hooks.mailinglist')
            assert self.__email_to
        return self.__email_to


def commit_info_list(*args):
    """Return a list of CommitInfo objects in chronological order.

    PARAMETERS
        Same as in the "git rev-list" command.
    """
    rev_info = git.rev_list(*args, pretty='format:%an <%ae>%n%s',
                            _split_lines=True, reverse=True)
    # Each commit should generate 3 lines of output.
    assert len(rev_info) % 3 == 0

    result = []
    prev_rev = None
    while rev_info:
        commit_keyword, rev = rev_info.pop(0).split(None, 1)
        author = rev_info.pop(0)
        subject = rev_info.pop(0)
        assert commit_keyword == 'commit'
        result.append(CommitInfo(rev, author, subject, prev_rev))
        prev_rev = rev

    return result
