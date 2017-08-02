"""Handling of branch creation."""

from errors import InvalidUpdate
from git import commit_oneline, git, file_exists
from updates.branches import branch_summary_of_changes_needed
from updates.branches.update import BranchUpdate

BRANCH_CREATION_EMAIL_BODY_TEMPLATE = """\
The branch '%(short_ref_name)s' was created%(in_namespace)s pointing to:

 %(commit_oneline)s"""


class BranchCreation(BranchUpdate):
    """Update class for branch creation.

    REMARKS
        Creation is a special case of update, and the implementation of
        some of the abstract methods would be identical.  So inherit
        from BranchUpdate.
    """
    def validate_ref_update(self):
        """See AbstractUpdate.validate_ref_update."""
        # First, perform the same validation as our parent class
        # (which means perform the same validation checks as for
        # branch updates).
        super(BranchCreation, self).validate_ref_update()

        self.__check_gitreview_defaultbranch()

    def get_update_email_contents(self):
        """See AbstractUpdate.get_update_email_contents.
        """
        # For branches, reference names normally start with refs/heads/.
        # If that's not the case, make the branch's namespace explicit.
        if self.ref_namespace in (None, 'refs/heads'):
            in_namespace = ''
        else:
            in_namespace = " in namespace '%s'" % self.ref_namespace

        subject = "[%s] Created branch '%s'%s" % (self.email_info.project_name,
                                                  self.short_ref_name,
                                                  in_namespace,)

        update_info = {'short_ref_name': self.short_ref_name,
                       'commit_oneline': commit_oneline(self.new_rev),
                       'in_namespace': in_namespace,
                       }
        body = BRANCH_CREATION_EMAIL_BODY_TEMPLATE % update_info
        if branch_summary_of_changes_needed(self.added_commits,
                                            self.lost_commits):
            body += self.summary_of_changes()

        return (self.everyone_emails(), subject, body)

    def __check_gitreview_defaultbranch(self):
        """If .gitreview exists, validate the defaultbranch value.

        This is meant to catch the situation where a user creates
        a new branch for a repository hosted on gerrit. Those
        repositories typically have a .gitreview file at their root,
        providing various information, one of them being the default
        branch name when sending patches for review. When creating
        a new branch, it is very easy (and frequent) for a user to
        forget to also update the .gitreview file, causing patch
        reviews to be sent with the wrong branch, which later then
        causes the patch to be merged (submitted) on the wrong
        branch once it is approved.

        We try to avoid that situation by reading the contents of
        those files at branch creation time, and reporting an error
        if it exists and points to a branch name different from ours.

        Note that we only do that for the traditional git branches.
        We don't worry about the branches in the gerrit-specific
        special namespaces, for which a user checking out the branch
        and sending a review is unlikely.
        """
        GITREVIEW_FILENAME = '.gitreview'
        DEFAULTBRANCH_CONFIG_NAME = 'gerrit.defaultbranch'

        # Only perform this check for traditional git branches.
        # See method description above for the reason why.
        if not self.ref_name.startswith('refs/heads/'):
            return

        if self.search_config_option_list('hooks.no-gitreview-check')\
                is not None:
            # The user explicitly disabled the .gitreview check
            # on this branch.
            return

        # If the file doesn't exist for that branch, then there is
        # no problem.
        if not file_exists(self.new_rev, GITREVIEW_FILENAME):
            return

        # Get the contents of the gitreview file, and then get git
        # to parse its contents. We process it all into a dictionary
        # rather than just query the value of the one config we are
        # looking for, for a couple of reasons:
        #   1. This allows us to avoid having to git returning with
        #      and error status when the file does not have the config
        #      entry we are looking for (git returns error code 1
        #      in that case);
        #   2. If we even want to look at other configurations in
        #      that file, the code is already in place to do so.

        gitreview_contents = git.show(
            '%s:%s' % (self.new_rev, GITREVIEW_FILENAME))
        gitreview_configs = git.config(
            '-z', '-l', '--file', '-',
            _input=gitreview_contents).split('\x00')

        config_map = {}
        for config in gitreview_configs:
            if not config:
                # "git config -z" adds a nul character at the end of
                # its output, which cause gitreview_configs to end with
                # an empty entry. Just ignore those.
                continue
            config_name, config_val = config.split('\n', 1)
            config_map[config_name] = config_val

        if DEFAULTBRANCH_CONFIG_NAME in config_map and \
                config_map[DEFAULTBRANCH_CONFIG_NAME] != self.short_ref_name:
            raise InvalidUpdate(
                "Incorrect gerrit default branch name in file `%s'."
                % GITREVIEW_FILENAME,
                "You probably forgot to update your %s file following"
                % GITREVIEW_FILENAME,
                "the creation of this branch.",
                '',
                "Please create a commit which updates the value",
                "of %s in the file `%s'"
                % (DEFAULTBRANCH_CONFIG_NAME, GITREVIEW_FILENAME),
                "and set it to `%s' (instead of `%s')."
                % (self.short_ref_name, config_map[DEFAULTBRANCH_CONFIG_NAME]))
