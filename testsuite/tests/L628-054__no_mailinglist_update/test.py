from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())
        self.assertTrue(p.status == 0, ex_run_image(p))

        expected_out = (
            # Confirmation that the update hooks called cvs_check...
            r".*cvs_check: `trunk/repo/a'"

            # The warning about the missing configuration variable.
            r".*The hooks.mailinglist config variable not set"
            r".*Commit emails will only be sent to"

            # An email should be sent to file-ci...
            r".*From: Test Suite <testsuite@example.com>" +
            r".*To: file-ci@gnat.com" +
            r".*Bcc: file-ci@gnat.com" +
            r".*Subject: \[repo\] Updated a" +
            r".*X-ACT-checkin: repo" +
            r".*X-Git-Refname: refs/heads/master" +
            r".*X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165" +
            r".*X-Git-Newrev: a60540361d47901d3fe254271779f380d94645f7" +

            # Confirmation that the update still went through.
            ".*master\s+->\s+master"
            )

        self.assertTrue(re.match(expected_out, p.out, re.DOTALL),
                        ex_run_image(p))

if __name__ == '__main__':
    runtests()
