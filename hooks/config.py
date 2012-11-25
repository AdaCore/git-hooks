from git import git, CalledProcessError

# A dictionary of all git config names that this module can query.
#   - The key used for this table is the config name.
#   - The value is another dictionary containing the following keys.
#       x 'type': The value is a string, and represents the type of
#                 of value our config parameter.  It should be either
#                 "bool", "int", "bool_or_int" or "path".
#                 This element is optional, in which case the type
#                 is assumed to be a simple string.
#       x 'default': The default value for this config option.

GIT_CONFIG_OPTS = {
    'hooks.allowdeletetag'   : { 'type' : 'bool', 'default' : 'false' },
    'hooks.allowNonFastForwardOnBranches' : {     'default' : ''},
    'hooks.allowlightweighttag' : { 'type' : 'bool', 'default' : 'false' },
    'hooks.combinedstylechecking' :
                               { 'type' : 'bool', 'default' : 'false' },
    'hooks.debuglevel'       : { 'type' : 'int',  'default' : '0' },
    'hooks.fromdomain'       : {                  'default' : None},
    'hooks.mailinglist'      : {                  'default' : None},
    'hooks.noemails'         : {                  'default' : ''},
}

class UnsupportedOptionName(Exception):
    """An exception raised when trying to lookup an unsupported option name.
    """
    pass

def git_config(option_name):
    """Get the repository or global option.

    Only the option names in GIT_CONFIG_OPTS are supported, and
    UnsupportedOptionName is raised if an unsupported option_name
    is passed.

    If the option is unset, return the default value, as provided
    by GIT_CONFIG_OPTS.

    PARAMETERS
        option_name: The name of the config option.
    """
    if option_name not in GIT_CONFIG_OPTS:
        raise UnsupportedOptionName(option_name)
    option_data = GIT_CONFIG_OPTS[option_name]

    kwargs = {}
    if 'type' in option_data:
        kwargs[option_data['type']] = True

    try:
        option_val = git.config(option_name, **kwargs)
    except CalledProcessError:
        # This option is probably not set in the config file.  Return
        # the default.
        option_val = option_data['default']
    return option_val
