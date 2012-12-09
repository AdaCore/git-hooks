"""The updates root module."""

from config import git_config
from git import git, get_object_type, is_null_rev, git_show_ref
from pre_commit_checks import check_commit
import re
from updates.emails import Email
from utils import debug


class AbstractUpdate(object):
    """An abstract class representing a reference update.

    ATTRIBUTES
        ref_name: The name of the reference being updated.
        short_ref_name: The reference's short name.  It is obtained by
            removing the "refs/[...]/" prefix.  For example, if ref_name
            is "refs/heads/master", then short_ref_name is "master".
        old_rev: The reference's revision (SHA1) prior to the update.
            A null revision means that this is a new reference.
        new_rev: The reference's revision (SHA1) after the update.
            A null revision means that this reference is being deleted.
        new_rev_type: The type of commit that new_rev points to.
            See git.get_object_type for more info.

    REMARKS
        This class is meant to be abstract and should never be instantiated.
    """
    def __init__(self, ref_name, old_rev, new_rev):
        """The constructor.

        Also calls self.auto_sanity_check() at the end.

        PARAMETERS
            ref_name: Same as the attribute.
            old_rev: Same as the attribute.
            new_rev: Same as the attribute.
        """
        m = re.match(r"refs/[^/]*/(.*)", ref_name)

        self.ref_name = ref_name
        self.short_ref_name = m.group(1) if m else ref_name
        self.old_rev = old_rev
        self.new_rev = new_rev
        self.new_rev_type = get_object_type(self.new_rev)

        self.self_sanity_check()

    def validate(self):
        """Raise InvalidUpdate if the update is invalid.

        This method verifies that the reference update itself is valid
        (by calling the validate_ref_update method), and then verifies
        that all the new commits introduced by this update passes
        style-checking.  Otherwise, raise InvalidUpdate.
        """
        debug('validate_ref_update (%s, %s, %s)'
              % (self.ref_name, self.old_rev, self.new_rev))
        self.validate_ref_update()
        self.pre_commit_checks()

    def send_email_notifications(self, email_info):
        """Send all email notifications associated to this update.
        """
        no_emails_list = git_config("hooks.noemails")
        if no_emails_list and self.ref_name in no_emails_list.split(","):
            print '-' * 75
            print "--  The hooks.noemails config parameter contains `%s'." \
                    % self.ref_name
            print "--  Commit emails will therefore not be sent."
            print '-' * 75
            return

        update_email_contents = self.get_update_email_contents(email_info)
        if update_email_contents is not None:
            (subject, body) = update_email_contents
            update_email = Email(email_info, subject, body,
                                 self.ref_name, self.old_rev, self.new_rev)
            update_email.send()

    def pre_commit_checks(self):
        """Run the pre-commit checks on this update's new commits.

        Determine the list of new commits introduced by this
        update, and perform the pre-commit-checks on them as
        appropriate.  Raise InvalidUpdate if one or more style
        violation was detected.
        """
        if is_null_rev(self.new_rev):
            # We are deleting a reference, so there cannot be any
            # new commit.
            return

        all_commits = expand_new_commit_to_list(self.new_rev)
        if len(all_commits) < 2:
            # There are no new commits, so nothing further to check.
            # Note: We check for len < 2 instead of 1, since the first
            # element is the "update base" commit (similar to the merge
            # base, where the commit is the common commit between the
            # 2 branches).
            return

        if git_config('hooks.combinedstylechecking') == 'true':
            # This project prefers to perform the style check on
            # the cumulated diff, rather than commit-per-commit.
            debug('(combined style checking)')
            all_commits = (all_commits[0], all_commits[-1])
        else:
            debug('(commit-per-commit style checking)')

        # Iterate over our list of commits in pairs...
        for (parent_rev, rev) in zip(all_commits[:-1], all_commits[1:]):
            check_commit(parent_rev, rev)

    #------------------------------------------------------------------
    #--  Abstract methods that must be overridden by child classes.  --
    #------------------------------------------------------------------

    def self_sanity_check(self):
        """raise an assertion failure if the init parameters are invalid...

        This method should check that the valud of the attributes created
        at initialization time correspond to values expected for the
        class.  For instance, a class that handles branch creation only
        should verify that the ref_name starts with 'refs/heads/' and
        that old_rev is null.

        REMARKS
            This method is abstract and should be overridden.
        """
        assert False

    def validate_ref_update(self):
        """Raise InvalidUpdate if the update is invalid.

        REMARKS
            This method is abstract and should be overridden.
        """
        assert False

    def get_update_email_contents(self, email_info):
        """Return a (subject, body) tuple describing the update (or None).

        This method should return a 2-element tuple to be used for
        creating an email describing the reference update, containing
        the following elements (in that order):
            - the email subject (a string);
            - the email body (a string).

        The email is meant to describe the type of update that was
        made.  For instance, for an annotated tag creation, the email
        should describe the name of the tag, the commit it points to,
        and perhaps the revision history associated to this tag.  For
        a branch update, the email should provide the name of the branch,
        the new commit it points to, and possibly a list of commits that
        are introduced by this update.

        This email should NOT, however, be confused with the emails
        that will be sent for each new commit introduced by this
        update.  Those emails are going to be taken care of separatly.

        Return None if a "cover" email is not going to be useful.
        For instance, if a branch update only introduces a few new
        commits, a branch update summary email is not going to bring
        much, and thus can be omitted.
        """
        assert False


def expand_new_commit_to_list(new_rev):
    """Expand the new commit into a list of commits introduced by the update.

    This function searches the "nearest" commit from one of the branches
    that already exist in the repository, and then generates a list of
    commits, starting with that "nearest" commit.  The list contains
    all the new commits leading to new_rev, in "chronological" order
    (parents first).

    If new_rev is a new headless branch with no common ancestor, then
    there is no "nearest" commit, and the first element of the list
    is set to None.

    REMARKS
        We treat branch updates different from new branches (where
        the old_rev is the null SHA), because branch updates can be
        non-fast-forward updates.  With such updates, the branch
        become completely unrelated to the old branch, or even
        an entirely new and headless branch, not connected to any
        of the already existing branches.  We could use simplified
        code for the easy fast-forward update, but that would be
        extra code to maintain.

    RETURN VALUE
        A list of commits.  The list will always contain at least
        one element, which is the "update base" commit (the commit
        that is common to an already-existing branch an our new_rev),
        or None.
    """
    # Start from the entire list of commits for our new branch, and
    # see if we can shorten that list a bit by finding an already
    # existing branch that has commits in common.
    commit_list = git.rev_list(new_rev, reverse=True, _split_lines=True)
    nearest_rev = None

    # For every existing reference, determine the number of commits
    # between that reference and new_rev.  Select the reference which
    # has the fewer number of commits.
    for (rev, _) in git_show_ref():
        rev_list_to_new_rev = git.rev_list(new_rev, '^%s' % rev,
                                           reverse=True, _split_lines=True)
        if len(rev_list_to_new_rev) < len(commit_list):
            nearest_rev = rev
            commit_list = rev_list_to_new_rev

    # If we found an already-existing reference that has common
    # ancestors with our new commit, then insert that common
    # commit at the start of our commit list.
    if nearest_rev is not None:
        commit_list.insert(0, git.merge_base(nearest_rev, new_rev))
    else:
        # This is most likely a new headless branch. Use None as
        # our convention to mean that the oldest commit is a root
        # commit (it has no parent).
        commit_list.insert(0, None)
    debug('update base: %s' % commit_list[0])

    return commit_list
