"""Handling of Git Notes updates."""

from config import git_config
from errors import InvalidUpdate
from git import git, is_null_rev, is_valid_commit
from updates import AbstractUpdate, RefKind
from updates.commits import commit_info_list
from updates.emails import Email
from updates.notes import GitNotes
from utils import indent

# The template to be used as the body of the email to be sent
# for a notes commit which either adds, or modifies a git notes.
UPDATED_NOTES_COMMIT_EMAIL_BODY_TEMPLATE = """\
A Git note has been updated; it now contains:

%(notes_contents)s

This note annotates the following commit:

%(annotated_rev_log)s
"""


# The template to be used as the body of the email to be sent
# for a notes commit which deletes a git notes.
DELETED_NOTES_COMMIT_EMAIL_BODY_TEMPLATE = """\
Git notes annotating the following commit have been deleted.

%(annotated_rev_log)s
"""


class NotesUpdate(AbstractUpdate):
    """Update object for Git Notes creation or update.

    The difference between Notes creation and Notes update is very
    small, so this class has been implemented in a way to support
    both (in other words, self.old_rev may be null).
    """
    def self_sanity_check(self):
        """See AbstractUpdate.self_sanity_check."""
        assert self.ref_kind == RefKind.notes_ref \
            and self.object_type == 'commit'
        assert self.ref_name.startswith('refs/notes/')

    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update."""
        # Only fast-forward changes are allowed.
        self.__ensure_fast_forward()

        # Also iterate over all new notes, and verify that
        # the associated commit is available. We need these
        # associated commits in order to create the emails
        # to be sent for those notes.
        for notes_commit in self.added_commits:
            notes = GitNotes(notes_commit.rev)
            if not is_valid_commit(notes.annotated_rev):
                error_message = [
                    'The commit associated to the following notes update',
                    'cannot be found. Please push your branch commits first',
                    'and then push your notes commits.',
                    '',
                    'Notes commit:     %s' % notes.rev,
                    'Annotated commit: %s' % notes.annotated_rev,
                    '',
                    'Notes contents:',
                    ] + \
                    notes.contents.splitlines()
                raise InvalidUpdate(*error_message)

    def pre_commit_checks(self):
        """See AbstractUpdate.pre_commit_checks."""
        # No pre-commit checks needed for Git Notes.
        pass

    def get_update_email_contents(self):
        """See AbstractUpdate.get_update_email_contents."""
        # No update email needed for notes (this is always
        # a fast-forward commit)...
        return None

    def email_commit(self, commit):
        """See AbstractUpdate.email_commit."""
        notes = GitNotes(commit.rev)

        # Get commit info for the annotated commit
        annotated_commit = commit_info_list("-1", notes.annotated_rev)[0]

        # Get a description of the annotated commit (a la "git show"),
        # except that we do not want the diff.
        #
        # Also, we have to handle the notes manually, as the commands
        # get the notes from the HEAD of the notes/commits branch,
        # whereas what we needs is the contents at the commit.rev.
        # This makes a difference when a single push updates the notes
        # of the same commit multiple times.
        annotated_rev_log = git.log(annotated_commit.rev, no_notes=True,
                                    max_count="1")
        notes_contents = (None if notes.contents is None
                          else indent(notes.contents, ' ' * 4))

        # Determine subject tag based on ref name:
        #   * remove "refs/notes" prefix
        #   * remove entire tag if remaining component is "commits"
        #     (case of the default refs/notes/commits ref)
        notes_ref = self.ref_name.split('/', 2)[2]
        if notes_ref == "commits":
            subject_tag = ""
        else:
            subject_tag = "(%s)" % notes_ref

        subject = '[notes%s][%s] %s' % (subject_tag,
                                        self.email_info.project_name,
                                        annotated_commit.subject)

        body_template = (
            DELETED_NOTES_COMMIT_EMAIL_BODY_TEMPLATE if notes_contents is None
            else UPDATED_NOTES_COMMIT_EMAIL_BODY_TEMPLATE)
        body = body_template % {
            'annotated_rev_log': annotated_rev_log,
            'notes_contents': notes_contents,
            }

        # Git commands calls strip on the output, which is usually
        # a good thing, but not in the case of the diff output.
        # Prevent this from happening by putting an artificial
        # character at the start of the format string, and then
        # by stripping it from the output.
        diff = git.show(commit.rev, pretty="format:|", p=True)[1:]

        email_bcc = git_config('hooks.filer-email')

        email = Email(self.email_info,
                      annotated_commit.email_to(self.ref_name), email_bcc,
                      subject, body, commit.full_author_email, self.ref_name,
                      commit.base_rev_for_display(), commit.rev, diff)
        email.enqueue()

    def __ensure_fast_forward(self):
        """Raise InvalidUpdate if the update is not a fast-forward update.
        """
        if is_null_rev(self.old_rev):
            # Git Notes creation, and thus necessarily a fast-forward.
            return

        # Non-fast-foward updates are characterized by the fact that
        # there is at least one commit that is accessible from the old
        # revision which would no longer be accessible from the new
        # revision.
        if git.rev_list("%s..%s" % (self.new_rev, self.old_rev)) == "":
            return

        raise InvalidUpdate(
            'Your Git Notes are not up to date.',
            '',
            'Please update your Git Notes and push again.')
