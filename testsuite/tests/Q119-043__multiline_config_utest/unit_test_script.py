import config

# Force the default "hooks.no-emails" to the empty tuple.
# That way, this unit test is independent of whatever default
# we actually use in real life.
config.GIT_CONFIG_OPTS["hooks.no-emails"]["default"] = ()

config.initialize_git_config_map()

no_emails = config.git_config("hooks.no-emails")
print("DEBUG: no-emails (len = {})".format(len(no_emails)))
print("\n--\n".join(no_emails))
