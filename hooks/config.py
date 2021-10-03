from errors import InvalidUpdate
from git import git, CalledProcessError
from type_conversions import to_type

import os
from subprocess import Popen, PIPE, STDOUT
from tempfile import mkstemp

# A list of regular expressions matching reference names created internally
# by gerrit.
# For instance, we know that gerrit creates creates a reference whose name
# is (quoting Gerrit's manual) "refs/changes/XX/YYYY/ZZ where YYYY is the
# numeric change number, ZZ is the patch set number and XX is the last two
# digits of the numeric change number", e.g.  refs/changes/20/884120/1
# This reference is just a kind of staging area. In this case, it ensures
# the newly-created commit has a reference, and therefore never ends up
# being garbage-collected.
GERRIT_INTERNAL_REFS = (
    "refs/changes/.*",
    "refs/users/.*/edit-.*",
)


# The name of the reference we use to store the repository-specific
# configuration for these hooks.
CONFIG_REF = "refs/meta/config"

# The name of the file we read the configuration from (stored in
# the special CONFIG_REF reference), relative to the repository's
# root directory.
CONFIG_FILENAME = "project.config"

# The commit to use in order to access the respository-specific
# configuration for these hooks. By default, it is CONFIG_REF.
# However, when a push is updating this reference, this global
# variable should be changed to the reference's new value, so
# telling this module to use the configuration using the latest
# commit, rather than the existing one.
config_commit = CONFIG_REF

# The default list of references for which no emails should be sent.
CONFIG_DEFAULT_NO_EMAILS = (
    # The reference that Gerrit uses to annotate commits with some info
    # from the code review performed on that commit (who performed
    # the review, when was the commit pushed, etc).
    #
    # We don't want to generate a commit email for these notes, because
    # they are pushed at the same time as the change it annotates.
    # Since a commit email is already being sent for the change itself,
    # and the annotation contains information that users rarely need
    # to consult, the email for the annotation was considered as unwanted
    # noise.
    "refs/notes/review",
)

# A dictionary of all git config names that this module can query.
#   - The key used for this table is the config name.
#   - The value is another dictionary containing the following keys.
#       + 'default': The default value for this config option.

GIT_CONFIG_OPTS = {
    "hooks.allow-delete-branch": {"default": (), "type": tuple},
    "hooks.allow-delete-tag": {"default": False, "type": bool},
    "hooks.allow-non-fast-forward": {"default": (), "type": tuple},
    "hooks.allow-lightweight-tag": {"default": False, "type": bool},
    "hooks.branch-ref-namespace": {"default": (), "type": tuple},
    "hooks.combined-style-checking": {"default": False, "type": bool},
    "hooks.commit-email-formatter": {"default": None},
    "hooks.commit-extra-checker": {"default": None},
    "hooks.commit-url": {"default": None},
    "hooks.debug-level": {"default": 0, "type": int},
    "hooks.email-new-commits-only": {"default": (), "type": tuple},
    "hooks.disable-email-diff": {"default": False, "type": bool},
    "hooks.disable-merge-commit-checks": {"default": False, "type": bool},
    "hooks.file-commit-cmd": {"default": None},
    "hooks.filer-email": {"default": (), "type": tuple},
    "hooks.from-domain": {"default": None},
    "hooks.frozen-ref": {"default": (), "type": tuple},
    "hooks.ignore-refs": {"default": GERRIT_INTERNAL_REFS, "type": tuple},
    "hooks.mailinglist": {"default": (), "type": tuple},
    "hooks.max-commit-emails": {"default": 100, "type": int},
    "hooks.max-email-diff-size": {"default": 100000, "type": int},
    "hooks.max-filepath-length": {"default": 150, "type": int},
    "hooks.max-rh-line-length": {"default": 76, "type": int},
    "hooks.no-emails": {"default": CONFIG_DEFAULT_NO_EMAILS, "type": tuple},
    "hooks.no-precommit-check": {"default": (), "type": tuple},
    "hooks.no-rh-character-range-check": {"default": False, "type": bool},
    "hooks.no-rh-style-checks": {"default": (), "type": tuple},
    "hooks.no-style-checks": {"default": (), "type": tuple},
    "hooks.pre-receive-hook": {"default": None},
    "hooks.post-receive-hook": {"default": None},
    "hooks.reject-merge-commits": {"default": (), "type": tuple},
    "hooks.rejected-branch-deletion-tip": {"default": None},
    "hooks.restrict-branch-deletion": {"default": False, "type": bool},
    "hooks.style-checker": {"default": "style_checker"},
    "hooks.style-checker-config-file": {"default": None},
    "hooks.tag-ref-namespace": {"default": (), "type": tuple},
    "hooks.tn-required": {"default": False, "type": bool},
    "hooks.update-hook": {"default": None},
    "hooks.use-standard-branch-ref-namespace": {"default": True, "type": bool},
    "hooks.use-standard-tag-ref-namespace": {"default": True, "type": bool},
}

# The maximum number of characters from a commit's subject
# to be used as part of the subject of emails describing
# the commit.
SUBJECT_MAX_SUBJECT_CHARS = 100


class ThirdPartyHook(object):
    """A script specified via a config option (and therefore project-specfic).

    This class aims at centralizing the handling of such options, so
    as to provide a consistent handling of these options.

    ATTRIBUTES
        hook_option_name: The name of the config option to use in order
            to get the path of the hook (if defined).
        hook_exe: The path to the hook itself (a string), or None if
            the project does not define that option.
    """

    def __init__(self, hook_option_name):
        """Initialize self.

        PARAMETERS
            hook_option_name: Same as the attribute.
        """
        self.hook_option_name = hook_option_name
        self.hook_exe = git_config(hook_option_name)

    @property
    def defined_p(self):
        """Return True if the project config set this hook, False if not."""
        return self.hook_exe is not None

    def call(self, hook_input=None, hook_args=None, cwd=None):
        """Call the script specified via self.hook_option_name.

        This method assumes that the repository's configuration
        defines a hook via the self.hook_option_name option.

        It calls that hook with the given argument.

        Raises InvalidUpdate if we failed to call the hook for whatever
        reason (typically, the hook's path does not exist, or we do not
        have the right permissions for us to execute it).

        PARAMETERS
            hook_input: A string, containing the data to be sent to
                the hook via its stdin stream. None if no data needs
                to be sent.
            hook_args: An iterable of command-line arguments to pass to
                the hook. None if no arguments are needed.
            cwd: The working directory from which to execute the hook.
                If None, the hook is executed from the current working
                directory.

        RETURN VALUE
            Return a tuple with the following elements:
              - The name of the script called as a hook;
              - The Popen object corresponding the script's execution
                (which, by the time this function returns, has finished
                executing);
              - The output of the script (stdout + stderr combined).
        """
        hook_cmd = [self.hook_exe]
        if hook_args is not None:
            hook_cmd.extend(hook_args)
        try:
            p = Popen(
                hook_cmd,
                stdin=PIPE if hook_input is not None else None,
                stdout=PIPE,
                stderr=STDOUT,
                cwd=cwd,
            )
        except OSError as E:
            raise InvalidUpdate(
                "Invalid {self.hook_option_name} configuration"
                " ({self.hook_exe}):\n"
                "{err_info}".format(self=self, err_info=str(E))
            )

        out, _ = p.communicate(hook_input)

        return (self.hook_exe, p, out)

    def call_if_defined(self, hook_input=None, hook_args=None, cwd=None):
        """If defined, call the script specified via self.hook_option_name.

        This is a convenience wrapper around self.call. This wrapper
        first checks whether the self.hook_option_name config is defined,
        and only then tries to call the associated hook. Otherwise,
        this method does nothing.

        PARAMETERS
            hook_input: Same as self.call.
            hook_args: Same as self.call.
            cwd: Same as self.call.

        RETURN VALUE
            If the self.hook_option_name config is defined, then returns
            the same as self.call. Otherwise, returns None.
        """
        if not self.defined_p:
            return
        return self.call(hook_input=hook_input, hook_args=hook_args, cwd=cwd)


class UnsupportedOptionName(Exception):
    """An exception raised when trying to lookup an unsupported option name."""

    pass


# A map containing the value of the various git config options.
# Lazy initialized.
#
# It includes all options listed in GIT_CONFIG_OPTS; if the project
# does not set a given option, then the default value is used in
# its place.
__git_config_map = None

CANNOT_FIND_CONFIG_FILE_ERROR = """\
-----------------------------------------------------------------
Unable to find the file {CONFIG_FILENAME} in {CONFIG_REF}.

Your repository appears to be incorrectly set up. Please contact
your repository's administrator to set your {CONFIG_FILENAME} file up.
-----------------------------------------------------------------
""".format(
    CONFIG_FILENAME=CONFIG_FILENAME, CONFIG_REF=CONFIG_REF
)


def git_config(option_name):
    """Return the git config value for option_name.

    PARAMETERS
        option_name: The name of the git config option to query.
    """
    global __git_config_map

    if option_name not in GIT_CONFIG_OPTS:
        raise UnsupportedOptionName(option_name)

    if __git_config_map is None:
        initialize_git_config_map()
    val = __git_config_map[option_name]

    # If this option as a 'type' specified, then convert it to
    # this type if necessary.  We do this here, rather than during
    # initialize_git_config_map to avoid the potential for causing
    # an error for options which might not be used in the end.
    if "type" in GIT_CONFIG_OPTS[option_name] and isinstance(val, str):
        try:
            val = to_type(val, GIT_CONFIG_OPTS[option_name]["type"])
        except ValueError:
            TYPE_NAME_MAP = {
                bool: "boolean",
                int: "integer",
                tuple: "list",
            }
            type_name = TYPE_NAME_MAP[GIT_CONFIG_OPTS[option_name]["type"]]
            raise InvalidUpdate(
                "Invalid %s value: %s (must be %s)" % (option_name, val, type_name)
            )
        # Save the converted value to avoid having to do it again
        # the next time we query the same config option.
        __git_config_map[option_name] = val

    return val


def initialize_git_config_map():
    """Initialize the __git_config_map global."""
    global __git_config_map

    # The hooks' configuration is stored in a special reference
    # (see CONFIG_REF), inside a file whose name is CONFIG_FILENAME.
    # Get that file.
    (tmp_fd, tmp_file) = mkstemp("tmp-git-hooks-")
    try:
        cfg_file = tmp_file
        try:
            git.show(config_commit + ":" + CONFIG_FILENAME, _outfile=tmp_fd)
        except CalledProcessError:
            # Either the CONFIG_REF reference does not exist, or
            # the config file itself does not exist. Either way,
            # it means that the repository has not been properly
            # set up for these hooks, which is a fatal error.
            raise InvalidUpdate(*CANNOT_FIND_CONFIG_FILE_ERROR.splitlines())
        os.close(tmp_fd)
        # Get the currently defined config values, all in one go.
        # Use "--file <cfg_file>" to make sure that we only parse
        # the file we just retrieved. Otherwise, git also parses
        # the user's config file.
        #
        # Also, use the nul character as the separator between each
        # entry (-z option) so as to not confuse them with potential
        # newlines being used inside the value of an option.
        all_configs = git.config("-z", "-l", "--file", cfg_file, _decode=True).split(
            "\x00"
        )
    finally:
        os.unlink(tmp_file)

    all_configs_map = {}
    for config in all_configs:
        if not config:
            # "git config -z" adds a nul character at the end of its output,
            # which cause all_configs to end with an empty entry. Just ignore
            # those.
            continue
        config_name, config_val = config.split("\n", 1)
        if (
            config_name in GIT_CONFIG_OPTS
            and "type" in GIT_CONFIG_OPTS[config_name]
            and GIT_CONFIG_OPTS[config_name]["type"] == tuple
        ):
            # This config is a list of potentially multiple values, and
            # therefore multiple entries with the same config name can be
            # provided for each value. Just save them in a list.
            if config_name not in all_configs_map:
                all_configs_map[config_name] = ()
            # Also, at least for now, we support coma-separated entries
            # for this multiple-value configs. So split each entry as well...
            config_val = to_type(config_val, tuple)
            all_configs_map[config_name] += config_val
        else:
            all_configs_map[config_name] = config_val

    # Populate the __git_config_map dictionary...
    __git_config_map = {}
    for config_name in GIT_CONFIG_OPTS.keys():
        # Get the config value from either the all_configs_map
        # if defined, or else from the default value.
        if config_name in all_configs_map:
            config_val = all_configs_map[config_name]
            if GIT_CONFIG_OPTS[config_name].get("type") == tuple:
                # Include the default values for this configuration to
                # the list of values provided by this project's config.
                # Otherwise, projects that just want to add to the default
                # would have to repeat that default in their repository's
                # configuration first before adding their own values,
                # as if starting the config option from scratch.
                config_val = GIT_CONFIG_OPTS[config_name]["default"] + config_val

        else:
            config_val = GIT_CONFIG_OPTS[config_name]["default"]

        # Finally, save the config value if __git_config_map
        __git_config_map[config_name] = config_val
