"""The updates root module."""

from config import git_config
from git import git, get_object_type, is_null_rev
from pre_commit_checks import check_commit
import re
from updates.emails import Email
from utils import debug, InvalidUpdate


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
        pre_update_refs: A GitReferences class (expected to contain
            the value of all references prior to the update being
            applied).

    REMARKS
        This class is meant to be abstract and should never be instantiated.
    """
    def __init__(self, ref_name, old_rev, new_rev, pre_update_refs):
        """The constructor.

        Also calls self.auto_sanity_check() at the end.

        PARAMETERS
            ref_name: Same as the attribute.
            old_rev: Same as the attribute.
            new_rev: Same as the attribute.
            pre_update_refs: Same as the attribute.
        """
        m = re.match(r"refs/[^/]*/(.*)", ref_name)

        self.ref_name = ref_name
        self.short_ref_name = m.group(1) if m else ref_name
        self.old_rev = old_rev
        self.new_rev = new_rev
        self.new_rev_type = get_object_type(self.new_rev)
        self.pre_update_refs = pre_update_refs

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

        commit_list = self.pre_update_refs.expand(self.old_rev, self.new_rev)
        if len(commit_list) < 2:
            # There are no new commits, so nothing further to check.
            # Note: We check for len < 2 instead of 1, since the first
            # element is the "update base" commit (similar to the merge
            # base, where the commit is the common commit between the
            # 2 branches).
            return

        # Check that the update wouldn't generate too many commit emails.
        # We know that commit emails would only be sent for commits which
        # are new for the repository, so we count those.
        if not self.in_no_emails_list():
            max_emails = int(git_config('hooks.maxcommitemails'))
            nb_emails = len([commit for commit in commit_list[1:]
                             if commit.new_in_repo])
            if nb_emails > max_emails:
                raise InvalidUpdate(
                    "This update introduces too many new commits (%d),"
                        " which would" % nb_emails,
                    "trigger as many emails, exceeding the"
                        " current limit (%d)." % max_emails,
                    "Contact your repository adminstrator if you really meant",
                    "to generate this many commit emails.")

        if git_config('hooks.combinedstylechecking') == 'true':
            # This project prefers to perform the style check on
            # the cumulated diff, rather than commit-per-commit.
            debug('(combined style checking)')
            commit_list = (commit_list[0], commit_list[-1])
        else:
            debug('(commit-per-commit style checking)')

        # Iterate over our list of commits in pairs...
        for (parent_commit, commit) in zip(commit_list[:-1], commit_list[1:]):
            if commit.new_in_repo:
                check_commit(parent_commit.rev, commit.rev)

    def send_email_notifications(self, email_info):
        """Send all email notifications associated to this update.
        """
        if self.in_no_emails_list():
            print '-' * 75
            print "--  The hooks.noemails config parameter contains `%s'." \
                    % self.ref_name
            print "--  Commit emails will therefore not be sent."
            print '-' * 75
            return
        self.email_ref_update(email_info)

    def email_ref_update(self, email_info):
        """Send the email describing to the reference update.

        This email can be seen as a "cover email", or a quick summary
        of the update that was performed.

        REMARKS
            The hooks may decide that such an email may not be necessary,
            and thus send nothing. See self.get_update_email_contents
            for more details.
        """
        update_email_contents = self.get_update_email_contents(email_info)
        if update_email_contents is not None:
            (subject, body) = update_email_contents
            update_email = Email(email_info, subject, body,
                                 self.ref_name, self.old_rev, self.new_rev)
            update_email.send()

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

    #-----------------------
    #--  Useful methods.  --
    #-----------------------

    def in_no_emails_list(self):
        """Return True if no emails should be sent for this reference update.
        """
        no_emails_list = git_config("hooks.noemails")
        return no_emails_list and self.ref_name in no_emails_list.split(",")
