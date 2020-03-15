"""A module related to these hooks's start up phase."""

import config


def init_all_globals(updated_refs):
    """Initialize all the global variables used by these hooks.

    PARAMETERS
        updated_refs: An OrderedDict, where the key is the name of
            a reference being updated, and the value is a tuple
            with the following elements:
                - The SHA1 of that reference prior to the update;
                - The SHA1 of that reference if the update is accepted.
    """
    # If config.CONFIG_REF is being modified, tell the config module
    # to use the reference's new value, instead of the old one.
    if config.CONFIG_REF in updated_refs:
        _, config.config_commit = updated_refs[config.CONFIG_REF]
