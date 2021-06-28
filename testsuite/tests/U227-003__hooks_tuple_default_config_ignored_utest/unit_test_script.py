import config

# Override whatever default the git-hooks uses for the "hooks.no-emails"
# config option in real life, just so as to make this unit test independent
# of that default.
UTEST_NO_EMAILS_DEFAULT = (
    "refs/what/ever",
    "refs/no/emails",
)
config.GIT_CONFIG_OPTS["hooks.no-emails"]["default"] = UTEST_NO_EMAILS_DEFAULT

# Get the project's effective configuration for the "hooks.no-emails"
# config. It should include both the default values (set above) and
# the values specified via the projet's git-hooks configuration.
no_emails = config.git_config("hooks.no-emails")
print("DEBUG: no-emails (len = {})".format(len(no_emails)))
print("\n".join(sorted(no_emails)))
