from gnatpython.fileutils import diff
from support import *

class TestRun(TestCase):
    def test_multiline_git_config(self):
        """Check that we handle multiline configs correctly
        """
        self.enable_unit_test()

        cd ('%s/bare/repo.git' % TEST_DIR)

        from config import initialize_git_config_map, git_config
        initialize_git_config_map()
        no_emails = git_config('hooks.no-emails')

        # no_emails should be 1-element tuple. Verify that and then
        # just keep that first element.
        self.assertEqual(
            len(no_emails), 1,
            'ERROR: hooks.no-emails should be 1 element only:\n%s'
            % str(no_emails))
        no_emails = no_emails[0]

        expected_no_emails = """\
a multiline description
of my project which should be
handled properly by the git-hooks."""
        self.assertEqual(expected_no_emails, no_emails,
                         '%s\n\nDiff:\n\n%s' % (
                             no_emails,
                             diff(expected_no_emails.splitlines(),
                                  no_emails.splitlines())))


if __name__ == '__main__':
    runtests()
