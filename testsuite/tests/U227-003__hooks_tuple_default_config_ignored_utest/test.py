from support import cd, runtests, TestCase, TEST_DIR


class TestRun(TestCase):
    def test_git_config(self):
        """Unit test AbstractUpdate child class missing methods.
        """
        cd('%s/repo' % TEST_DIR)
        self.enable_unit_test()

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
        self.assertEqual(
            sorted(no_emails),
            [
                "refs/heads/uninteresting",
                "refs/no/emails",
                "refs/what/ever",
            ],
        )


if __name__ == '__main__':
    runtests()
