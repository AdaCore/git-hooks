"""Management of git commits during updates..."""

from git import git, commit_parents, empty_tree_rev
from config import git_config


class CommitInfo(object):
    """A git commit.

    ATTRIBUTES
        rev: The commit's revision (SHA1).
        author: The author of the commit.
        subject: The subject of the commit.
        parent_revs: A list of revisions (SHA1s) of the parents
            of this commit.  The empty list if the commit has
            no parent.  None if this attribute has not been
            computed.
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
    def __init__(self, rev, author, subject, parent_revs):
        self.rev = rev
        self.author = author
        self.subject = subject
        self.parent_revs = parent_revs
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

    def base_rev_for_display(self):
        """The rev as reference to determine what changed in this commit.

        RETURN VALUE
            The reference commit's SHA1, or None if this commit does not
            have a parent (root commit).
        """
        # Make sure we use each commits's first parent as the base
        # commit.  This is important for merge commits, or commits
        # imported by merges.
        #
        # Consider for instance the following scenario...
        #
        #                    <-- origin/master
        #                   /
        #    C1 <-- C2 <-- C3 <-- M4 <-- master
        #      \                  /
        #        <-- B1 <-- B2 <-+
        #
        # ... where the user merged his changes B1 & B2 into
        # his master branch (as commit M4), and then tries
        # to push this merge.
        #
        # There are 3 new commits in this case to be checked,
        # which are B1, B2, and M4, with C3 being the update's
        # base rev.
        #
        # If not careful, we would be checking B1 against C3,
        # rather than C1, which would cause these scripts
        # to think that all the files modified by C2 and C3
        # have been modified by B1, and thus must be checked.
        #
        # Similarly, we would be checking M4 against B2,
        # whereas it makes more sense in that case to be
        # checking it against C3.
        if self.parent_revs is None:
            self.parent_revs = commit_parents(self.rev)
        if self.parent_revs:
            return self.parent_revs[0]
        else:
            return None

    def base_rev_for_git(self):
        """The rev as reference to determine what changed in this commit.

        Use this function when this rev should be passed to git commands,
        as it never returns None.

        RETURN VALUE
            The reference commit's SHA1, or the empty tree's SHA1 if
            this commit does not have a parent (root commit).
        """
        base_rev = self.base_rev_for_display()
        if base_rev is None:
            base_rev = empty_tree_rev()
        return base_rev


def commit_info_list(*args):
    """Return a list of CommitInfo objects in chronological order.

    PARAMETERS
        Same as in the "git rev-list" command.
    """
    rev_info = git.rev_list(*args, pretty='format:%P%n%an <%ae>%n%s',
                            _split_lines=True, reverse=True)
    # Each commit should generate 4 lines of output.
    assert len(rev_info) % 4 == 0

    result = []
    while rev_info:
        commit_keyword, rev = rev_info.pop(0).split(None, 1)
        parents = rev_info.pop(0).split()
        author = rev_info.pop(0)
        subject = rev_info.pop(0)
        assert commit_keyword == 'commit'
        result.append(CommitInfo(rev, author, subject, parents))

    return result
