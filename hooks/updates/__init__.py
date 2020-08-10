"""The updates root module."""

from config import (git_config, SUBJECT_MAX_SUBJECT_CHARS, ThirdPartyHook,
                    CONFIG_FILENAME, CONFIG_REF)
from copy import deepcopy
from enum import Enum
from errors import InvalidUpdate
import json
from git import git, is_null_rev, commit_parents, commit_rev
from os.path import expanduser, isfile, getmtime
from pre_commit_checks import (check_revision_history, style_check_commit,
                               check_filename_collisions,
                               reject_commit_if_merge)
import re
import shlex
import sys
from syslog import syslog
import time
from updates.commits import commit_info_list
from updates.emails import EmailCustomContents, EmailInfo, Email
from updates.mailinglists import expanded_mailing_list
from utils import debug, warn, get_user_name, indent, ref_matches_regexp


# The different kinds of references we handle.
#
# Note: We try to list the entries in order of frequency, with more
# frequent updates first. That way, anytime some code iterates over
# this enum, it'll get the more frequent update first.
class RefKind(Enum):
    # A branch. The vast majority of updates will be branch updates.
    branch_ref = "branch"
    # A special branch used to hold git notes.
    notes_ref = "notes"
    # A tag reference (either annotated or lightweight).
    tag_ref = "tag"


# The different types of reference updates.
class UpdateKind(Enum):
    # A new reference being created;
    create = 1
    # An existing reference being deleted;
    delete = 2
    # An existing reference being updated (it already existed before,
    # and its value is being changed).
    update = 3


class AbstractUpdate(object):
    """An abstract class representing a reference update.

    ATTRIBUTES
        ref_name: The name of the reference being updated.
        short_ref_name: The reference's short name.  It is obtained by
            removing the "refs/[...]/" prefix.  For example, if ref_name
            is "refs/heads/master", then short_ref_name is "master".
        ref_namespace: The part of the reference name prior to
            the short_ref_name (excluding the separating '/').
            It can be None if the namespace could not be parsed out of
            the ref_name, in which case short_ref_name should be equal
            to ref_name.
        ref_kind: The kind of reference being updated (a RefKind object).
        object_type: A string, indicating the type of object pointed at
            by the reference being updated (using self.new_rev unless
            the reference is being deleted, in which case we use
            self.old_rev instead). See "git cat-file -t" for more
            information.
        old_rev: The reference's revision (SHA1) prior to the update.
            A null revision means that this is a new reference.
        new_rev: The reference's revision (SHA1) after the update.
            A null revision means that this reference is being deleted.
        all_refs: A dictionary containing all references, as described
            in git_show_ref.
        email_info: An EmailInfo object.  See REMARKS below.
        added_commits: A list of CommitInfo objects added by our update.
        lost_commits: A list of CommitInfo objects lost after our update.

    REMARKS
        This class is meant to be abstract and should never be instantiated.

        Regarding the "email_info" attribute: This object is not strictly
        required during the "update" phase.  However, instantiating it
        allows for two things:
            1. The instantiation itself verifies that the repository
               provides the minimum configuration required to send
               email notifications, and raise an InvalidUpdate exception
               if not.
            2. It contains some information which is used repeatedly
               (Eg: the module name can be queries every time a file
               is style-checked). We will use this object to provide
               this required information, rather than recomputing it
               repeatedly.
    """
    def __init__(self, ref_name, ref_kind, object_type, old_rev, new_rev,
                 all_refs, submitter_email):
        """The constructor.

        Also calls self.auto_sanity_check() at the end.

        PARAMETERS
            ref_name: Same as the attribute.
            ref_kind: Same as the attribute.
            object_type: Same as the attribute.
            old_rev: Same as the attribute.
            new_rev: Same as the attribute.
            all_refs: Same as the attribute.
            submitter_email: Same as parameter from_email in class
                EmailInfo's constructor.
                This is used to override the default "from" email when
                the user sending the emails is different from the user
                that pushed/submitted the update.
        """
        # If the repository's configuration does not provide
        # the minimum required to email update notifications,
        # refuse the update.
        if not git_config('hooks.mailinglist'):
            raise InvalidUpdate(
                'Error: hooks.mailinglist config option not set.',
                'Please contact your repository\'s administrator.')

        m = re.match(r"([^/]+/[^/]+)/(.+)", ref_name)

        self.ref_name = ref_name
        self.short_ref_name = m.group(2) if m else ref_name
        self.ref_namespace = m.group(1) if m else None
        self.ref_kind = ref_kind
        self.object_type = object_type
        self.old_rev = old_rev
        self.new_rev = new_rev
        self.all_refs = all_refs
        self.email_info = EmailInfo(email_from=submitter_email)

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
        self.__reject_frozen_ref_update()
        self.validate_ref_update()
        self.__check_max_commit_emails()
        self.pre_commit_checks()

    def send_email_notifications(self):
        """Send all email notifications associated to this update.
        """
        no_email_re = self.search_config_option_list('hooks.no-emails')
        if no_email_re is not None:
            warn(*['-' * 70,
                   "--  The hooks.no-emails config option contains `%s',"
                   % no_email_re,
                   '--  which matches the name of the reference being'
                   ' updated ',
                   '--  (%s).' % self.ref_name,
                   '--',
                   '--  Commit emails will therefore not be sent.',
                   '-' * 70,
                   ], prefix='')
            return
        # This phase needs all added commits to have certain attributes
        # to be computed.  Do it now.
        self.__set_send_email_p_attr(self.added_commits)
        self.__email_ref_update()
        self.__email_new_commits()

    # ------------------------------------------------------------------
    # --  Abstract methods that must be overridden by child classes.  --
    # ------------------------------------------------------------------

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

    def get_update_email_contents(self):
        """Return a tuple describing the update (or None).

        This method should return a 3-element tuple to be used for
        creating an email describing the reference update, containing
        the following elements (in that order):
            - the email distribution list (an iterable);
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

    # ------------------------------------------------------------------
    # --  Methods that child classes may override.                    --
    # ------------------------------------------------------------------

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

        # Check to see if any of the entries in hooks.no-precommit-check
        # might be matching our reference name...
        for exp in git_config('hooks.no-precommit-check'):
            exp = exp.strip()
            if re.match(exp, self.ref_name):
                # Pre-commit checks are explicitly disabled on this branch.
                debug("(hooks.no-precommit-check match: `%s')" % exp)
                return

        if self.__no_cvs_check_user_override():
            # Just return. All necessary traces have already been
            # handled by the __no_cvs_check_user_override method.
            return

        # Create a list of commits that were added, but with revert
        # commits being filtered out. We have decided that revert commits
        # should not be subject to any check (QB08-047).  This allows
        # users to quickly revert a commit if need be, without having
        # to worry about bumping into any check of any kind.
        added = self.added_commits
        for commit in added:
            if commit.is_revert():
                debug('revert commit detected,'
                      ' all checks disabled for this commit: %s' % commit.rev)
                added.remove(commit)

        if not added:
            # There are no new commits, so nothing further to check.
            return

        # Determine whether we should be doing RH style checking...
        do_rh_style_checks = (
            self.search_config_option_list('hooks.no-rh-style-checks')
            is None)

        # Perform the revision-history of all new commits, unless
        # specifically disabled by configuration.
        #
        # Done separately from the rest of the pre-commit checks,
        # which check the files changed by the commits, because of
        # the case where hooks.combined-style-checking is true;
        # we do not want to forget checking the revision history
        # of some of the commits.
        if do_rh_style_checks:
            for commit in added:
                if not commit.pre_existing_p:
                    check_revision_history(commit)

        reject_merge_commits = (
            self.search_config_option_list('hooks.reject-merge-commits')
            is not None)
        if reject_merge_commits:
            for commit in added:
                reject_commit_if_merge(commit, self.ref_name)

        # Perform the filename-collision checks.  These collisions
        # can cause a lot of confusion and fustration to the users,
        # so do not provide the option of doing the check on the
        # final commit only (following hooks.combined-style-checking).
        # Do it on all new commits.
        for commit in added:
            if not commit.pre_existing_p:
                check_filename_collisions(commit)

        self.call_project_specific_commit_checker()

        self.__do_style_checks()

    def get_standard_commit_email(self, commit):
        """Return an Email object for the given commit.

        Here, "standard" means that the Email returned corresponds
        to the Email the git-hooks sends by default, before any
        possible project-specific customization is applied.

        Before sending this email, users of this method are expected
        to apply those customizations as needed.

        PARAMETERS
            commit: A CommitInfo object.
        """
        if self.ref_namespace in ('refs/heads', 'refs/tags'):
            if self.short_ref_name == 'master':
                branch = ''
            else:
                branch = '/%s' % self.short_ref_name
        else:
            # Unusual namespace for our reference. Use the reference
            # name in full to label the branch name.
            branch = '(%s)' % self.ref_name

        subject = '[%(repo)s%(branch)s] %(subject)s' % {
            'repo': self.email_info.project_name,
            'branch': branch,
            'subject': commit.subject[:SUBJECT_MAX_SUBJECT_CHARS],
            }

        # Generate the body of the email in two pieces:
        #   1. The commit description without the patch;
        #   2. The diff stat and patch.
        # This allows us to insert our little "Diff:" marker that
        # bugtool detects when parsing the email for filing (this
        # part is now performed by the Email class). The purpose
        # is to prevent bugtool from searching for TNs in the patch
        # itself.
        #
        # For the diff, there is one subtlelty:
        # Git commands calls strip on the output, which is usually
        # a good thing, but not in the case of the diff output.
        # Prevent this from happening by putting an artificial
        # character at the start of the format string, and then
        # by stripping it from the output.

        body = git.log(commit.rev, max_count="1") + '\n'
        if git_config('hooks.commit-url') is not None:
            url_info = {'rev': commit.rev,
                        'ref_name': self.ref_name}
            body = (git_config('hooks.commit-url') % url_info +
                    '\n\n' +
                    body)

        if git_config('hooks.disable-email-diff'):
            diff = None
        else:
            diff = git.show(commit.rev, p=True, M=True, stat=True,
                            pretty="format:|")[1:]

        filer_cmd = git_config('hooks.file-commit-cmd')
        if filer_cmd is not None:
            filer_cmd = shlex.split(filer_cmd)

        email_bcc = git_config('hooks.filer-email')

        return Email(self.email_info,
                     commit.email_to(self.ref_name), email_bcc,
                     subject, body, commit.full_author_email,
                     self.ref_name, commit.base_rev_for_display(),
                     commit.rev, diff, filer_cmd=filer_cmd)

    # -----------------------
    # --  Useful methods.  --
    # -----------------------

    def human_readable_ref_name(self, action=None,
                                default_namespace='refs/heads'):
        """Return a human-readable image (string) of our reference.

        This function returns a string describing self.ref_name
        in a way that's easier for users to grasp:

          "'" {short_name} "'" [ action ] [ "in namespace '" {namespace} "'" ]

        PARAMETERS
            action: If not None, the "action" part of the returned image.
                Otherwise, the "action" section of the return image
                is simply skipped.
            default_namespace: The namespace that is used by default
                for the kind of reference that self.ref_name is.
                We use this to determine whether or not the returned
                image needs to specify the namespace of our reference,
                or whether it can be omitted.
        """
        if action is None:
            action = ''
        else:
            action = ' {}'.format(action)

        # For references that are ourside the given default_namespace,
        # make the namespace explicit.
        if self.ref_namespace in (None, default_namespace):
            loc = ''
        else:
            loc = " in namespace '{}'".format(self.ref_namespace)

        return "'{short_ref_name}'{action}{loc}".format(
            short_ref_name=self.short_ref_name, action=action, loc=loc)

    def search_config_option_list(self, option_name, ref_name=None):
        """Search the given config option as a list, and return the first match.

        This function first extracts the value of the given config,
        expecting it to be a list of regular expressions.  It then
        iterates over that list until it finds one that matches
        REF_NAME.

        PARAMETERS
            option_name: The name of the config option to be using
                as the source for our list of regular expressions.
            ref_name: The name of the reference used for the search.
                If None, use self.ref_name.

        RETURN VALUE
            The first regular expression matching REF_NAME, or None.
        """
        if ref_name is None:
            ref_name = self.ref_name
        ref_re_list = git_config(option_name)
        for ref_re in ref_re_list:
            ref_re = ref_re.strip()
            if ref_matches_regexp(ref_name, ref_re):
                return ref_re
        return None

    def get_refs_matching_config(self, config_name):
        """Return the list of references matching the given config option."""
        result = []
        for ref_name in self.all_refs.keys():
            if self.search_config_option_list(config_name,
                                              ref_name) is not None:
                result.append(ref_name)
        return result

    def summary_of_changes(self):
        """A summary of changes to be added at the end of the ref-update email.

        Note that we used to display the list of commits twice:
        First in a list of one-line representations, as an overview;
        and then a second time, displaying the same list where each
        commit is printed in full (minus the diff itself).

        We found that the second list made the emails much too large,
        for information that wasn't considered useful in general,
        and easily reconstructed on demand if needed.  So we dropped
        the second list entirely.

        We could have kept a shorter version of the second list, but
        the only potentially useful info that we would have gotten
        out of it is really the author and committer of each email.
        Since this has been considered marginal in usefulness,
        we did not choose this option.

        One option for the future is to make this email entirely
        configurable, one way or the other. We are not providing
        this functionality for now, because there hasn't been
        any demand for it. There is also value in having a certain
        amount of consistency across projects.

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
            for commit in reversed(self.lost_commits):
                # Note: See this function's description for the reasons
                # behind only displaying the list of commits using
                # their oneline representation.
                summary.append('  ' + commit.oneline_str())

        if self.added_commits:
            has_silent = False
            summary.append('')
            summary.append('')
            summary.append('Summary of changes (added commits):')
            summary.append('-----------------------------------')
            summary.append('')
            # Note that we want the summary to include all commits
            # now accessible from this reference, not just the new
            # ones.
            for commit in reversed(self.added_commits):
                if commit.send_email_p:
                    marker = ''
                else:
                    marker = ' (*)'
                    has_silent = True
                # Note: See this function's description for the reasons
                # behind only displaying the list of commits using
                # their oneline representation.
                summary.append('  ' + commit.oneline_str() + marker)

            # If we added a ' (*)' marker to at least one commit,
            # add a footnote explaining what it means.
            if has_silent:
                summary.extend([
                    '',
                    '(*) This commit exists in a branch whose name matches',
                    '    the hooks.noemail config option. No separate email',
                    '    sent.'])

        # We do not want that summary to be used for filing purposes.
        # So add a "Diff:" marker.
        if summary:
            # We know that the output starts with a couple of
            # empty strings. To avoid too much of a break between
            # the "Diff:" marker and the rest of the summary,
            # replace the first empty line with our diff marker
            # (instead of pre-pending it, for instance).
            summary[0] = '\n\nDiff:'

        return '\n'.join(summary)

    def everyone_emails(self):
        """Return the list of email addresses listing everyone possible.
        """
        return expanded_mailing_list(self.ref_name, None)

    # ------------------------
    # --  Private methods.  --
    # ------------------------

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

    @property
    def send_cover_email_to_filer(self):
        """True iff the cover email should be sent to hooks.filer-email

        By default, the cover email is just an informational email
        which is not specific to any particular TN, and thus should
        not be filed. So return False by default.
        """
        return False

    def commit_data_for_hook(self, commit):
        """Return a dict with information about the given commit.

        The intention for this dictionary is to be passed to thirdparty
        hooks written by repository owners (see, for instance, the
        hooks.commit-extra-checker config option). We want to provide
        all the information we already have, so the hook doesn't have
        to recompute that information again.

        The contents of this dictionary follows what's documented in
        README.md for the hooks.commit-extra-checker config option.

        PARAMETERS
            commit: A CommitInfo object.
        """
        return {
            "rev": commit.rev,
            "ref_name": self.ref_name,
            "ref_kind": self.ref_kind.value,
            "object_type": self.object_type,
            "author_name": commit.author_name,
            "author_email": commit.author_email,
            "subject": commit.subject,
            "body": commit.raw_revlog,
        }

    def call_project_specific_commit_checker(self):
        """Call hooks.commit-extra-checker for all added commits (if set).

        Raise InvalidUpdate with the associated error message if the hook
        returned nonzero. Just print the hook's output otherwise.
        """
        commit_checker_hook = ThirdPartyHook("hooks.commit-extra-checker")
        if not commit_checker_hook.defined_p:
            return

        for commit in self.added_commits:
            hook_exe, p, out = commit_checker_hook.call(
                hook_input=json.dumps(self.commit_data_for_hook(commit)),
                hook_args=(self.ref_name, commit.rev),
            )
            if p.returncode != 0:
                raise InvalidUpdate(
                    "The following commit was rejected by your"
                    " hooks.commit-extra-checker script"
                    " (status: {p.returncode})".format(p=p),
                    "commit: {commit.rev}".format(commit=commit),
                    *out.splitlines())
            else:
                sys.stdout.write(out)

    def __get_added_commits(self):
        """Return a list of CommitInfo objects added by our update.

        RETURN VALUE
            A list of CommitInfo objects, or the empty list if
            the update did not introduce any new commit.
        """
        if is_null_rev(self.new_rev):
            return []

        # Compute the list of commits that are not accessible from
        # any of the references.  These are the commits which are
        # new in the repository.
        #
        # Note that we do not use the commit_info_list function for
        # that, because we only need the commit hashes, and a list
        # of commit hashes is more convenient for what we want to do
        # than a list of CommitInfo objects.

        exclude = ['^%s' % self.all_refs[ref_name]
                   for ref_name in self.all_refs.keys()
                   if ref_name != self.ref_name]
        if not is_null_rev(self.old_rev):
            exclude.append('^%s' % self.old_rev)

        new_repo_revs = git.rev_list(self.new_rev, *exclude, reverse=True,
                                     _split_lines=True)

        # If this is a reference creation (base_rev is null), try to
        # find a commit which can serve as base_rev.  We try to find
        # a pre-existing commit making the base_rev..new_rev list
        # as short as possible.
        base_rev = self.old_rev
        if is_null_rev(base_rev):
            if len(new_repo_revs) > 0:
                # The ref update brings some new commits.  The first
                # parent of the oldest of those commits, if it exists,
                # seems like a good candidate.  If it does not exist,
                # we are pushing an entirely new headless branch, and
                # base_rev should remain null.
                parents = commit_parents(new_repo_revs[0])
                if parents:
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
        # accessible from the old_rev, but not from any of the references.

        exclude = ['^%s' % self.all_refs[rev]
                   for rev in self.all_refs.keys()]
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
               % {'rev': self.new_rev,
                  'repo': self.email_info.project_name,
                  'user': get_user_name(),
                  'no_cvs_check_fullpath': no_cvs_check_fullpath,
                  })
        return True

    def __check_max_commit_emails(self):
        """Raise InvalidUpdate is this update will generate too many emails.
        """
        # Check that the update wouldn't generate too many commit emails.

        if self.search_config_option_list('hooks.no-emails') is not None:
            # This repository was configured to skip emails on this branch.
            # Nothing to do.
            return

        # We know that commit emails would only be sent for commits which
        # are new for the repository, so we count those.

        self.__set_send_email_p_attr(self.added_commits)
        nb_emails = len([commit for commit in self.added_commits
                         if commit.send_email_p])
        max_emails = git_config('hooks.max-commit-emails')
        if nb_emails > max_emails:
            raise InvalidUpdate(
                "This update introduces too many new commits (%d),"
                " which would" % nb_emails,
                "trigger as many emails, exceeding the"
                " current limit (%d)." % max_emails,
                "Contact your repository adminstrator if you really meant",
                "to generate this many commit emails.")

    def __do_style_checks(self):
        if self.search_config_option_list('hooks.no-style-checks') is not None:
            # The respository has been configured to disable all style
            # checks on this branch.
            debug('no style check on this branch (hooks.no-style-checks)')
            return

        added = self.__added_commits
        if git_config('hooks.combined-style-checking'):
            # This project prefers to perform the style check on
            # the cumulated diff, rather than commit-per-commit.
            # Behave as if the update only added one commit (new_rev),
            # with a single parent being old_rev.  If old_rev is nul
            # (branch creation), then use the first parent of the oldest
            # added commit.
            debug('(combined style checking)')
            if not added[-1].pre_existing_p:
                base_rev = (
                    added[0].base_rev_for_git() if is_null_rev(self.old_rev)
                    else self.old_rev)
                style_check_commit(base_rev, self.new_rev,
                                   self.email_info.project_name)
        else:
            debug('(commit-per-commit style checking)')
            # Perform the pre-commit checks, as needed...
            for commit in added:
                if not commit.pre_existing_p:
                    style_check_commit(commit.base_rev_for_git(), commit.rev,
                                       self.email_info.project_name)

    def __email_ref_update(self):
        """Send the email describing to the reference update.

        This email can be seen as a "cover email", or a quick summary
        of the update that was performed.

        REMARKS
            The hooks may decide that such an email may not be necessary,
            and thus send nothing. See self.get_update_email_contents
            for more details.
        """
        update_email_contents = self.get_update_email_contents()

        if update_email_contents is not None:
            (email_to, subject, body) = update_email_contents
            email_bcc = (git_config('hooks.filer-email')
                         if self.send_cover_email_to_filer else None)
            update_email = Email(self.email_info,
                                 email_to, email_bcc, subject, body, None,
                                 self.ref_name, self.old_rev, self.new_rev)
            update_email.enqueue()

    def __maybe_get_email_custom_contents(self, commit,
                                          default_subject,
                                          default_body,
                                          default_diff):
        """Return an EmailCustomContents for the given commit, if applicable.

        For projects that define the hooks.commit-email-formatter config
        option, this method calls the script it points to, and builds
        an EmailCustomContents object from the data returned by the script.

        Errors are handled as gracefully as possible, by returning
        an EmailCustomContents which only changes the body of the email
        by adding a warning section describing the error that occurred.

        Returns None if the hooks.commit-email-formatter is not defined
        by the project.

        PARAMETERS
            commit: A CommitInfo object.
            default_subject: The email's subject to use by default
                unless overriden by the commit-email-formatter hook.
            default_body: The email's body to use by default, unless
                overriden by the commit-email-formatter hook.
            default_diff: The email's "Diff:" section to use by default,
                unless overriden by the commit-email-formatter hook.
        """
        email_contents_hook = ThirdPartyHook("hooks.commit-email-formatter")
        if not email_contents_hook.defined_p:
            return None

        hooks_data = self.commit_data_for_hook(commit)
        hooks_data["email_default_subject"] = default_subject
        hooks_data["email_default_body"] = default_body
        hooks_data["email_default_diff"] = default_diff

        hook_exe, p, out = email_contents_hook.call(
            hook_input=json.dumps(hooks_data),
            hook_args=(self.ref_name, commit.rev),
        )

        def standard_email_due_to_error(err_msg):
            """Return an EmailCustomContents with the given err_msg.

            This function allows us to perform consistent error handling
            when trying to call the hooks.commit-email-formatter script.
            It returns an EmailCustomContents where nothing is changed
            (and therefore the standard email gets sent) except for
            the addition of a warning section at the end of the email's
            body (just before the "Diff:" section). This warning section
            indicates that an error was detected, and provides information
            about it.

            PARAMETERS
                err_msg: A description of the error that occurred (a string).
            """
            appendix = "WARNING:\n" \
                "{err_msg}\n" \
                "Falling back to default email format.\n" \
                "\n" \
                "$ {hook_exe} {update.ref_name}" \
                " {commit.rev}\n" \
                "{out}\n".format(
                    err_msg=err_msg, hook_exe=hook_exe, update=self,
                    commit=commit, out=out)
            return EmailCustomContents(
                appendix=indent(appendix, "| "),
                diff=default_diff)

        if p.returncode != 0:
            return standard_email_due_to_error(
                "hooks.commit-email-formatter returned nonzero:"
                " {p.returncode}.".format(p=p))

        try:
            contents_data = json.loads(out)
        except ValueError:
            return standard_email_due_to_error(
                "hooks.commit-email-formatter returned invalid JSON.")

        if not isinstance(contents_data, dict):
            return standard_email_due_to_error(
                "hooks.commit-email-formatter output is not JSON dict.")

        return EmailCustomContents(
            subject=contents_data.get("email_subject"),
            body=contents_data.get("email_body"),
            diff=contents_data.get("diff", default_diff))

    def __send_commit_email(self, commit, standard_email):
        """Send the email for the given commit.

        PARAMETERS
            commit: A CommitInfo object.
            standard_email: An Email object, containing the standard email
                for the given commit (see self.get_standard_commit_email).
        """
        email = standard_email
        custom_email_contents = self.__maybe_get_email_custom_contents(
            commit=commit,
            default_subject=email.email_subject,
            default_body=email.email_body,
            default_diff=email.diff)
        if custom_email_contents is not None:
            # Create a new Email object with the requested customizations.
            email = deepcopy(standard_email)
            if custom_email_contents.subject is not None:
                email.email_subject = custom_email_contents.subject
            if custom_email_contents.body is not None:
                email.email_body = custom_email_contents.body
            if custom_email_contents.appendix is not None:
                email.email_body += "\n" + custom_email_contents.appendix
            email.diff = custom_email_contents.diff

        email.enqueue()

    def __email_new_commits(self):
        """Send one email per new (non-pre-existing) commit.
        """
        for commit in self.added_commits:
            if commit.send_email_p:
                self.__send_commit_email(
                    commit, self.get_standard_commit_email(commit))

    def __set_send_email_p_attr(self, commit_list):
        # Make sure we have at least one commit in the list.  Otherwise,
        # nothing to do.
        if not commit_list:
            return

        # Determine the list of commits accessible from NEW_REV, after
        # having excluded all commits accessible from the branches
        # matching the hooks.no-emails hooks config.  These are the
        # non-excluded commits, ie the comments whose attribute
        # should be set to True.
        exclude = ['^%s' % ref_name for ref_name
                   in self.get_refs_matching_config('hooks.no-emails')]
        base_rev = commit_list[0].base_rev_for_display()
        if base_rev is not None:
            # Also reduce the list already present in this branch
            # prior to the update.
            exclude.append('^%s' % base_rev)
        included_refs = git.rev_list(self.new_rev, *exclude,
                                     _split_lines=True)

        # Also, we always send emails for first-parent commits.
        # This is useful in the following scenario:
        #
        #   - The repository has a topic/feature branch for which
        #     there is a no-email configuration;
        #   - When ready to "merge" his topic/feature branch to master,
        #     the user first rebases it, and pushes the new topic/feature
        #     branch. Because the push is for a no-emails branch, commit
        #     emails are turned off (as expected).
        #   - The user then merges the topic/feature branch into
        #     master, and pushes the new master branch.
        #
        # Unless we ignore the hooks.no-emails config for first-parent
        # commits, we end up never sending any commit emails for the
        # commits being pushed on master. This is not what we want,
        # here, because the commits aren't really comming from an
        # external source.  We want to disable commit emails while
        # the commits are being worked on the topic/feature branch,
        # but as soon as they make it to tracked branches, a commit
        # email should be sent.
        first_parents_expr = [self.new_rev]
        if base_rev is not None:
            first_parents_expr.append('^%s' % base_rev)
        first_parents = git.rev_list(*first_parents_expr, first_parent=True,
                                     _split_lines=True)

        for commit in commit_list:
            commit.send_email_p = (commit.rev in included_refs or
                                   commit.rev in first_parents)

    def __reject_frozen_ref_update(self):
        """Raise InvalidUpdate if trying to update a frozen branch.

        PARAMETERS:
            short_ref_name: The reference's short name (see short_ref_name
                attribute in class AbstractUpdate).

        REMARKS
            Frozen and retired mean the same thing, in this case, except
            we use a {CONFIG_FILENAME}-based approach to determining whether
            updates are allowed on this branch or not. Eventually, we
            might probably retire reject_retired_branch_update...
        """
        frozen_refs = git_config('hooks.frozen-ref')
        for frozen_ref in frozen_refs:
            if self.ref_name != frozen_ref.strip():
                continue
            # Reject the update. Try to provide a more user-friendly
            # message for the majority of the cases where the user
            # is trying to update a branch, but still handle the case
            # where the user is updating an arbitrary reference.
            if self.ref_name.startswith('refs/heads/'):
                info = {'who': 'the %s branch' % self.short_ref_name,
                        'what': 'branch'}
            else:
                info = {'who': self.ref_name,
                        'what': 'reference'}
            raise InvalidUpdate(
                'Updates to %(who)s are no longer allowed because' % info,
                'this %(what)s is now frozen (see "hooks.frozen-ref" in file'
                % info,
                '{CONFIG_FILENAME}, from the special branch {CONFIG_REF}).'
                .format(CONFIG_FILENAME=CONFIG_FILENAME,
                        CONFIG_REF=CONFIG_REF))
