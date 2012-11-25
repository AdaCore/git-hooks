from support import *
import re

class TestRun(TestCase):
    def test_push_tag(self):
        """Try pushing a new value for an annotated tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that each commit gets checked individually.
        os.environ['GIT_HOOKS_DEBUG_LEVEL'] = '1'

        # Push "full-tag". This tag has a new value, different from
        # that is on the remote.  We should get an email notification,
        # and a warning about how bad it is to do that.
        expected_out = (
            # The warning about the dangers of modifying a published tag.
            r".*IMPORTANT NOTICE:" +
            r'.*You just updated the "full-tag" tag as follow:' +
            r".*  old SHA1: a69eaaba59ea6d7574a9c5437805a628ea652c8e" +
            r".*  new SHA1: 17b9d4acf8505cd1da487ad62e37819b93779a27" +

            # This push introduces one new commit, so we expect the
            # associated cvs_check traces as well.
            r".*DEBUG: check_commit\(" +
                "old_rev=354383fa06047ef8053782410c221341e4b07ec4, " +
                "new_rev=8c0b4151f9f41efcaeb70ea6f91158e4605aaeda\)" +
            r".*cvs_check: `trunk/repo/bar\.c'" +
            r".*cvs_check: `trunk/repo/foo'" +

            # The header of the notification email that should be sent...
            r".*From: Test Suite <testsuite@example.com>" +
            r".*To: repo@example.com" +
            r".*Bcc: file-ci@gnat.com" +
            r".*Subject: \[repo\] Updated tag full-tag" +
            r".*X-ACT-checkin: repo" +
            r".*X-Git-Refname: refs/tags/full-tag" +
            r".*X-Git-Oldrev: a69eaaba59ea6d7574a9c5437805a628ea652c8e" +
            r".*X-Git-Newrev: 17b9d4acf8505cd1da487ad62e37819b93779a27" +

            # The body of that email...
            r".*The signed tag 'full-tag' was updated" +
            r".*8c0b415\.\.\. Added bar\.c, and updated foo\." +
            r".*It previously pointed to:" +
            r".*354383f\.\.\. Initial commit\." +
            r".*Tagger: Joel Brobecker <brobecker@adacore.com>" +
            r".*Date: Thu Jun 28 11:50:36 2012 -0700" +
            r".*Tag a commit that makes more sense\." +

            # Output from git that confirms that the tag was updated.
            r".*a69eaab\.\.17b9d4a\s+full-tag\s+->\s+full-tag"
            )

        p = Run('git push origin full-tag'.split())
        self.assertEqual(p.status, 0, ex_run_image(p))
        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))


if __name__ == '__main__':
    runtests()
