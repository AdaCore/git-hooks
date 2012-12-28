from git import git

# A dictionary of all git config names that this module can query.
#   - The key used for this table is the config name.
#   - The value is another dictionary containing the following keys.
#       + 'default': The default value for this config option.

GIT_CONFIG_OPTS = \
    {'hooks.allow-delete-tag':         {'default': 'false'},
     'hooks.allow-non-fast-forward':   {'default': ''},
     'hooks.allow-lightweight-tag':    {'default': 'false'},
     'hooks.combined-style-checking':  {'default': 'false'},
     'hooks.debug-level':              {'default': '0'},
     'hooks.from-domain':              {'default': None},
     'hooks.mailinglist':              {'default': None},
     'hooks.max-commit-emails':        {'default': '100'},
     'hooks.no-emails':                {'default': ''},
     'hooks.no-precommit-check':       {'default': ''},
     'hooks.tn-required':              {'default': 'false'},

     # The following options are for testing purposes only, and should
     # never be used in an operational repository.
     'hooks.bcc-file-ci':              {'default': 'true'},
    }

# The maximum number of characters from a commit's subject
# to be used as part of the subject of emails describing
# the commit.
SUBJECT_MAX_SUBJECT_CHARS = 100


class UnsupportedOptionName(Exception):
    """An exception raised when trying to lookup an unsupported option name.
    """
    pass


# A map containing the value of the various git config options.
# Lazy initialized.
#
# It includes all options listed in GIT_CONFIG_OPTS; if the project
# does not set a given option, then the default value is used in
# its place.
__git_config_map = None


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

    return __git_config_map[option_name]


def initialize_git_config_map():
    """Initialize the __git_config_map global.
    """
    global __git_config_map

    # Get the currently defined config values, all in one go.
    all_configs = git.config('-l', _split_lines=True)
    all_configs_map = dict([config.split('=', 1) for config in all_configs])

    # Populate the __git_config_map dictionary...
    __git_config_map = {}
    for config_name in GIT_CONFIG_OPTS.keys():
        config_info = GIT_CONFIG_OPTS[config_name]

        # Get the config value from either the all_configs_map
        # if defined, or else from the default value.
        if config_name in all_configs_map:
            config_val = all_configs_map[config_name]
        else:
            config_val = GIT_CONFIG_OPTS[config_name]['default']

        # Finally, save the config value if __git_config_map
        __git_config_map[config_name] = config_val
