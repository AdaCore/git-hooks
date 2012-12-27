"""The updates root module."""

from config import git_config, SUBJECT_MAX_SUBJECT_CHARS
from copy import deepcopy
from git import (git, get_object_type, is_null_rev, commit_parents,
                 commit_rev, get_module_name)
from os import environ
from os.path import expanduser, isfile, getmtime
from pre_commit_checks import check_commit
import re
from syslog import syslog
import time
from updates.commits import commit_info_list
from updates.emails import Email
from utils import debug, InvalidUpdate, warn, get_user_name

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
        added_commits: A list of CommitInfo objects added by our update.
        lost_commits: A list of CommitInfo objects lost after our update.

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

        # Implement the added_commits "attribute" as a property,
        # to allow for initialization only on-demand. This allows
        # us to avoid computing this list until the moment we
        # actually need it. To help caching its value, avoiding
        # the need to compute it multiple times, we introduce
        # a private attribute named __added_commits.
        #
        # Same treatment for the lost_commits "attribute".
        self.__added_commits = None
        self.__lost_commits = None

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

        PARAMETERS
            email_info: An EmailInfo object.
        """
        if self.in_no_emails_list():
            print '-' * 75
            print "--  The hooks.no-emails config parameter contains `%s'." \
                    % self.ref_name
            print "--  Commit emails will therefore not be sent."
            print '-' * 75
            return
        self.__email_ref_update(email_info)
        self.__email_new_commits(email_info)

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

        PARAMETERS
            email_info: An EmailInfo object.
        """
        assert False

    #------------------------------------------------------------------
    #--  Methods that child classes may override.                    --
    #------------------------------------------------------------------

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

        excluded_branches = git_config('hooks.no-precommit-check')
        if (excluded_branches
            and self.ref_name in excluded_branches.split(',')):
            # Pre-commit checks are explicitly disabled on this branch.
            debug('(%s in hooks.no-precommit-check)' % self.ref_name)
            return

        if self.__no_cvs_check_user_override():
            # Just return. All necessary traces have already been
            # handled by the __no_cvs_check_user_override method.
            return

        added = self.added_commits
        if not added:
            # There are no new commits, so nothing further to check.
            return

        # Check that the update wouldn't generate too many commit emails.
        # We know that commit emails would only be sent for commits which
        # are new for the repository, so we count those.
        if not self.in_no_emails_list():
            max_emails = int(git_config('hooks.max-commit-emails'))
            nb_emails = len([commit for commit in added
                             if not commit.pre_existing_p])
            if nb_emails > max_emails:
                raise InvalidUpdate(
                    "This update introduces too many new commits (%d),"
                        " which would" % nb_emails,
                    "trigger as many emails, exceeding the"
                        " current limit (%d)." % max_emails,
                    "Contact your repository adminstrator if you really meant",
                    "to generate this many commit emails.")

        if git_config('hooks.combined-style-checking') == 'true':
            # This project prefers to perform the style check on
            # the cumulated diff, rather than commit-per-commit.
            debug('(combined style checking)')
            combined_commit = added[-1]
            combined_commit.base_rev = added[0].base_rev
            added = [combined_commit,]
        else:
            debug('(commit-per-commit style checking)')

        # Iterate over our list of commits in pairs...
        for commit in added:
            if not commit.pre_existing_p:
                check_commit(commit.base_rev, commit.rev)

    def email_commit(self, email_info, commit):
        """Send an email describing the given commit.

        PARAMETERS
            email_info: An EmailInfo object.
            commit: A CommitInfo object.
        """
        subject = '[%(repo)s%(branch)s] %(subject)s' % {
            'repo' : email_info.project_name,
            'branch' : '/%s' % self.short_ref_name
                if self.short_ref_name != 'master' else '',
            'subject' : commit.subject[:SUBJECT_MAX_SUBJECT_CHARS],
            }

        # Generate the body of the email in two passes:
        #   1. The commit description without the patch;
        #   2. The diff stat and patch.
        # This allows us to insert our little "Diff:" marker that
        # bugtool detects when parsing the email for filing.
        # The purpose is to prevent bugtool from searching for
        # TNs in the patch itself.
        body = git.log(commit.rev, max_count="1")
        body += '\n\n'
        body += git.show(commit.rev, p=True, M=True, stat=True,
                         pretty="format:%nDiff:%n")

        email = Email(email_info, subject, body, self.ref_name,
                      commit.base_rev, commit.rev)
        email.send()

    #-----------------------
    #--  Useful methods.  --
    #-----------------------

    def in_no_emails_list(self):
        """Return True if no emails should be sent for this reference update.
        """
        no_emails_list = git_config("hooks.no-emails")
        return no_emails_list and self.ref_name in no_emails_list.split(",")

    def summary_of_changes(self):
        """A summary of changes to be added at the end of the ref-update email.

        PARAMETERS
            None.

        RETURN VALUE
            A string containing the summary of changes.
        """
        summary = []
        # Display the lost commits (if any) first, to increase
        # our chances of attracting the reader's attention.
        if self.lost_commits:
            summary.append('')
            summary.append('')
            summary.append('!!! WARNING: THE FOLLOWING COMMITS ARE'
                           ' NO LONGER ACCESSIBLE (LOST):')
            summary.append('--------------------------------------'
                           '-----------------------------')
            summary.append('')
            for commit in self.lost_commits:
                summary.append('  ' + commit.oneline_str())

        if self.added_commits:
            has_pre_existing = False
            summary.append('')
            summary.append('')
            summary.append('Summary of changes (added commits):')
            summary.append('-----------------------------------')
            summary.append('')
            # Note that we want the summary to include all commits
            # now accessible from this reference, not just the new
            # ones.
            for commit in self.added_commits:
                has_pre_existing = has_pre_existing or commit.pre_existing_p
                marker = ' (*)' if commit.pre_existing_p else ''
                summary.append('  ' + commit.oneline_str() + marker)

            # If we added a ' (*)' marker to at least one commit,
            # add a footnote explaining what it means.
            if has_pre_existing:
                summary.append('')
                summary.append('(*) This commit already existed in another '
                               'branch/reference.')
                summary.append('     No separate email sent.')

        return '\n'.join(summary)

    #------------------------
    #--  Private methods.  --
    #------------------------

    @property
    def added_commits(self):
        """The added_commits attribute, lazy initialized."""
        if self.__added_commits is None:
            self.__added_commits = self.__get_added_commits()
        return self.__added_commits

    @property
    def lost_commits(self):
        """The lost_commits attribute, lazy initialized."""
        if self.__lost_commits is None:
            self.__lost_commits = self.__get_lost_commits()
        return self.__lost_commits

    def __get_added_commits(self):
        """Return a list of CommitInfo objects added by our update.

        RETURN VALUE
            A list of CommitInfo objects, or the empty list if
            the update did not introduce any new commit.
        """
        if is_null_rev(self.new_rev):
            return []

        exclude = ['^%s' % self.pre_update_refs.refs[ref_name]
                   for ref_name in self.pre_update_refs.refs.keys()]
        base_rev = self.old_rev

        # Compute the list of commits that are not accessible from
        # any of the references.  These are the commits which are
        # new in the repository.
        #
        # Note that we do not use the commit_info_list function for
        # that, because we only need the commit hashes, and a list
        # of commit hashes is more convenient for what we want to do
        # than a list of CommitInfo objects.
        new_repo_revs = git.rev_list(self.new_rev, *exclude, reverse=True,
                                     _split_lines=True)

        # If this is a reference creation (base_rev is null), try to
        # find a commit which can serve as base_rev.  We try to find
        # a pre-existing commit making the base_rev..new_rev list
        # as short as possible.
        if is_null_rev(base_rev):
            if len(new_repo_revs) > 0:
                # The ref update brings some new commits.  The first
                # parent of the oldest of those commits, if it exists,
                # seems like a good candidate.  If it does not exist,
                # we are pushing a entirely new headless branch, and
                # base_rev should remain null.
                parents = commit_parents(new_repo_revs[0])
                if parents is not None:
                    base_rev = parents[0]
            else:
                # This reference update does not bring any new commits
                # at all. This means new_rev is already accessible
                # through one of the references, thus making it a good
                # base_rev as well.
                base_rev = self.new_rev

        # Expand base_rev..new_rev to compute the list of commits which
        # are new for the reference.  If there is no actual base_rev
        # (Eg. a headless branch), then expand to all commits accessible
        # from that reference.
        if not is_null_rev(base_rev):
            commit_list = commit_info_list(self.new_rev, '^%s' % base_rev)
            base_rev = commit_rev(base_rev)
        else:
            commit_list = commit_info_list(self.new_rev)
            base_rev = None
        if commit_list:
            commit_list[0].base_rev = base_rev

        # Iterate over every commit, and set their pre_existing_p attribute.
        for commit in commit_list:
            commit.pre_existing_p = commit.rev not in new_repo_revs

        debug('update base: %s' % base_rev)

        return commit_list

    def __get_lost_commits(self):
        """Return a list of CommitInfo objects lost after our update.

        RETURN VALUE
            A list of CommitInfo objects, or the empty list if
            the update did not cause any commit to be lost.
        """
        if is_null_rev(self.old_rev):
            # We are creating a new reference, so we cannot possibly
            # be losing commits.
            return []

        # The list of lost commits is computed by listing all commits
        # accessible from the old_rev, but not from either the new rev
        # nor any of the other references.

        # First, create new GitReferences were the reference has
        # the new value.  This will allow us to use it to generate
        # the exclude list without having to handle this reference
        # by hand.
        refs_copy = deepcopy(self.pre_update_refs)
        refs_copy.update_ref(self.ref_name, self.new_rev)

        # Compute the list of commits accessible from old_rev but
        # not from refs_copy.  This is our list of lost commits.
        exclude = ['^%s' % refs_copy.refs[rev]
                   for rev in refs_copy.refs.keys()]
        commit_list = commit_info_list(self.old_rev, *exclude)

        return commit_list

    def __no_cvs_check_user_override(self):
        """Return True iff pre-commit-checks are turned off by user override...

        ... via the ~/.no_cvs_check file.

        This function also performs all necessary debug traces, warnings,
        etc.
        """
        no_cvs_check_fullpath = expanduser('~/.no_cvs_check')
        # Make sure the tilde expansion worked.  Since we are only using
        # "~" rather than "~username", the expansion should really never
        # fail...
        assert (not no_cvs_check_fullpath.startswith('~'))

        if not isfile(no_cvs_check_fullpath):
            return False

        # The no_cvs_check file exists.  Verify its age.
        age = time.time() - getmtime(no_cvs_check_fullpath)
        one_day_in_seconds = 24 * 60 * 60

        if (age > one_day_in_seconds):
            warn('%s is too old and will be ignored.' % no_cvs_check_fullpath)
            return False

        debug('%s found - pre-commit checks disabled' % no_cvs_check_fullpath)
        syslog('Pre-commit checks disabled for %(rev)s on %(repo)s by user'
               ' %(user)s using %(no_cvs_check_fullpath)s'
               % {'rev' : self.new_rev,
                  'repo' : get_module_name(),
                  'user' : get_user_name(),
                  'no_cvs_check_fullpath' : no_cvs_check_fullpath,
                 })
        return True


    def __email_ref_update(self, email_info):
        """Send the email describing to the reference update.

        This email can be seen as a "cover email", or a quick summary
        of the update that was performed.

        PARAMETERS
            email_info: An EmailInfo object.

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

    def __email_new_commits(self, email_info):
        """Send one email per new (non-pre-existing) commit.

        PARAMETERS
            email_info: An EmailInfo object.
        """
        for commit in self.added_commits:
            if not commit.pre_existing_p:
                self.email_commit(email_info, commit)
