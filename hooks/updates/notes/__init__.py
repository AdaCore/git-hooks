"""Git Notes updates root module."""

from git import git, CalledProcessError, diff_tree


class GitNotes(object):
    """An object representing a Git Notes change.

    ATTRIBUTES
        rev: The revision of the notes change.
        filename: The name of the file in the notes/commits branch
            used to store the contents of the notes.
        contents: The contents of the git notes.  None if the notes
            have been removed.
        annotated_rev: The revision of the commit being annotated.
    """

    def __init__(self, notes_rev):
        """The constructor.

        PARAMETERS
            notes_rev: The revision of the notes change.
        """
        self.rev = notes_rev
        self.filename = self.__get_notes_filename(notes_rev)
        # Implement the contents "attribute" as a property.
        # This allows us to lazy-initialize it.  And use
        # a private attribute name __contents to cache its value.
        self.__contents = None
        self.annotated_rev = self.filename.replace("/", "")

    @property
    def contents(self):
        """The contents "attribute", lazily initialized."""
        if self.__contents is None:
            self.__contents = self.__get_notes_contents(self.rev, self.filename)
        return self.__contents

    @classmethod
    def __get_notes_filename(cls, notes_rev):
        """Return the filename used to store the git notes.

        PARAMETERS
            notes_rev: The revision of the notes change.
        """
        # A git note for any given commit (called the "annotated commit"
        # in this function) is maintained through a file in the special
        # refs/notes/commits namespace.  The name of that file seems
        # to vary a little bit from case to case (sometimes it is just
        # equal to "%s" % rev, while some other times it is equal to
        # "%s/%s" % (rev[:2], rev[2:]) where rev is the revision of
        # the annotated commit. The one constant is that it is easy
        # to deduce the annotated commit ID, by just stripping the '/'
        # characters.

        # Look at the files modified by the git notes commit via
        # diff-tree. There should be only one, pointing us towards
        # the annotated commit.
        all_changes = diff_tree("-r", notes_rev)
        if not all_changes:
            # notes_rev is probably the root commit.  Just use the empty
            # tree's sha1 as the reference.
            empty_tree_rev = git.mktree(_input="")
            all_changes = diff_tree("-r", empty_tree_rev, notes_rev)

        # The output should be 2 lines...
        #   - The first line contains the hash of what is being compared,
        #     which should be notes_rev;
        #   - The second line contains the file change that interests us.
        # ... except in the case where the notes_rev does not have
        # a parent (first note).  In that case, we diff-tree'ed against
        # the empty tree rev, and the first line is omitted.
        #
        # Normally, there should only be one entry returned by diff_tree.
        # However, there is a situation where the output is more than
        # one entry: Newer version of git sometimes rename some of the
        # files created by older versions of "git notes" during notes
        # updates, and bunches those renamings together with a note
        # update, thus creating commits that actually touch multiple
        # files (N707-041). In that situation, it appears as though
        # the first entry is always the one corresponding to the commit
        # being annotated, so discard anything past the first line.
        assert all_changes

        (_, _, _, _, _, filename) = all_changes[0]
        return filename

    @classmethod
    def __get_notes_contents(cls, notes_rev, notes_filename):
        """Return the contents of the notes at notes_rev.

        PARAMETERS
            notes_rev: The revision of the notes change.
            notes_filename: The filename containing the notes.
        """
        try:
            return git.show("%s:%s" % (notes_rev, notes_filename))
        except CalledProcessError:
            # The note was probably deleted, so no more notes.
            return None
