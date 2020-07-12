"""Management of git commits during updates..."""

from git import git, empty_tree_rev, diff_tree
from updates.mailinglists import expanded_mailing_list
from utils import debug


class CommitInfo(object):
    """A git commit.

    ATTRIBUTES
        rev: The commit's revision (SHA1).
        author_name: The author of the commit.
        author_email: The email address of the author of the commit.
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
    """
    def __init__(self, rev, author_name, author_email, subject, parent_revs):
        self.rev = rev
        self.author_name = author_name
        self.author_email = author_email
        self.subject = subject
        self.parent_revs = parent_revs
        self.pre_existing_p = None
        self.send_email_p = None

        # A cache for the raw_revlog and the raw_revlog_lines methods.
        self.__raw_revlog = None
        self.__raw_revlog_lines = None

        # A cache for the "email_to" method.
        self.__email_to = {}

        # A cache for the "files_changed" method.
        self.__files_changed = None

    def oneline_str(self):
        """A one-line string description of the commit.
        """
        return '%s... %s' % (self.rev[:7], self.subject[:59])

    @property
    def full_author_email(self):
        """Return the author's full email address (name and actual address)."""
        return '{self.author_name} <{self.author_email}>'.format(self=self)

    @property
    def raw_revlog(self):
        """Return the commit's raw revlog.

        This is what Git calls the commit's "raw body (unwrapped subject
        and lines)".

        Note that the revlog is computed lazily and then cached.
        """
        if self.__raw_revlog is None:
            self.__raw_revlog = git.log(self.rev, max_count='1',
                                        pretty='format:%B')
        return self.__raw_revlog

    @property
    def raw_revlog_lines(self):
        """Return the commit's raw revlog split into lines.

        This is what Git calls the commit's "raw body (unwrapped subject
        and lines)".

        Note that the revlog and its split into lines is computed
        lazily and then cached.
        """
        if self.__raw_revlog_lines is None:
            self.__raw_revlog_lines = self.raw_revlog.splitlines()
        return self.__raw_revlog_lines

    def email_to(self, ref_name):
        """Return this commit's list of email recipients.

        Returns a list of email addresses, in RFC 822 format.

        PARAMETERS
            ref_name: The name of the reference being updated.

        Implemented as a property in order for its initialization
        to be performed only when required.
        """
        if ref_name not in self.__email_to:
            self.__email_to[ref_name] = expanded_mailing_list(
                ref_name, self.files_changed)
        return self.__email_to[ref_name]

    def files_changed(self):
        """Return the list of files changed by this commit.

        Cache the result in self.__files_changed so that subsequent
        calls to this method do not require calling git again.
        """
        if self.__files_changed is None:
            self.__files_changed = []
            all_changes = diff_tree('-r', self.base_rev_for_git(), self.rev)
            for item in all_changes:
                (old_mode, new_mode, old_sha1, new_sha1, status, filename) \
                    = item
                debug('diff-tree entry: %s %s %s %s %s %s'
                      % (old_mode, new_mode, old_sha1, new_sha1, status,
                         filename),
                      level=5)
                self.__files_changed.append(filename)
        return self.__files_changed

    def base_rev_for_display(self):
        """The rev as reference to determine what changed in this commit.

        This method assumes that self.parent_revs is not None, and raises
        an assertion failure if the assumption is not met.  Users can call
        function `commit_parents' to set it if needed.

        RETURN VALUE
            The reference commit's SHA1, or None if this commit does not
            have a parent (root commit).
        """
        assert self.parent_revs is not None

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

    def is_revert(self):
        """Return True if this commit appears to be a revert commit.

        We detect such commits by searching for specific patterns that
        the "git revert" command automatically includes in the default
        revision log of such commits, hoping that a user is not deleting
        them afterwards.
        """
        if 'This reverts commit' in self.raw_revlog:
            return True

        # No recognizable pattern. Probably not a revert commit.
        return False


def commit_info_list(*args):
    """Return a list of CommitInfo objects in chronological order.

    PARAMETERS
        Same as in the "git rev-list" command.
    """
    rev_info = git.rev_list(*args, pretty='format:%P%n%an%n%ae%n%s',
                            _split_lines=True, reverse=True)
    # Each commit should generate 5 lines of output.
    assert len(rev_info) % 5 == 0

    result = []
    while rev_info:
        commit_keyword, rev = rev_info.pop(0).split(None, 1)
        parents = rev_info.pop(0).split()
        author_name = rev_info.pop(0)
        author_email = rev_info.pop(0)
        subject = rev_info.pop(0)
        assert commit_keyword == 'commit'
        result.append(CommitInfo(rev, author_name, author_email, subject,
                                 parents))

    return result
