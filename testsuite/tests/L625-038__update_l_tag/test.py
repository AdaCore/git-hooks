from support import *
import re

class TestRun(TestCase):
    def test_delete_lightweight_tag(self):
        """Try updating a lightweight tag.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that each commit gets checked individually.
        self.set_debug_level(1)

        p = Run('git push origin some-tag'.split())
        self.assertEqual(p.status, 0, ex_run_image(p))

        expected_out = (
            # Check that the warning about the pitfalls of changing
            # the value of a tag is emitted and contains the important
            # information (tag name, old rev, new rev)...
            r".*IMPORTANT NOTICE:" +
            r".*You just updated the \"some-tag\" tag as follow:" +
            r".*old SHA1: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e" +
            r".*new SHA1: 8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5" +
            # This push introduces a new commit, so verify the associated
            # cvs_check traces...
            r".*DEBUG: check_commit\(" +
                r"old_rev=8b9a0d6bf08d7a983affbee3c187adadaaedec9e, " +
                r"new_rev=8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5\)" +
            # Check the contents of the email notification.
            r".*From: Test Suite <testsuite@example.com>" +
            r".*To: something-ci@example.com" +
            r".*Bcc: file-ci@gnat.com" +
            r".*Subject: \[repo\] Updated tag some-tag" +
            r".*X-ACT-checkin: repo" +
            r".*X-Git-Refname: refs/tags/some-tag" +
            r".*X-Git-Oldrev: 8b9a0d6bf08d7a983affbee3c187adadaaedec9e" +
            r".*X-Git-Newrev: 8a567a0e4b4c1a13b2b5cba2fdaf981db9d356b5" +
            r".*The lightweight tag 'some-tag' was updated to point to:" +
            r".*8a567a0\.\.\. Put some contents in file `a'\." +
            r".*It previously pointed to:" +
            r".*8b9a0d6\.\.\. New file: a\." +
            # And check git's output confirm that the tag was updated.
            r".*\s+8b9a0d6\.\.8a567a0\s+some-tag\s+->\s+some-tag")
        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
