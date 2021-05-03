from support import *

class TestRun(TestCase):
    def test_push_commits(self):
        """See comments below.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push not-ok-104 on master. It introduces a new commit
        # where one line in the RH is 104 characters long. It should
        # still be accepted, since we've explicitly configured
        # the repository to skip RH line-length checks.
        p = Run('git push origin not-ok-104:master'.split())
        expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] 104 characters. Way too long.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 8f9e357b53cc88eb0e7a57ee8c7d1ccd74db1ae3
remote:
remote: commit 8f9e357b53cc88eb0e7a57ee8c7d1ccd74db1ae3
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     104 characters. Way too long.
remote:
remote:     00000000011111111112222222222333333333344444444445555555555666666666677777777778888888888999999999900000
remote:     12345678901234567890123456789012345678901234567890123456789012345678901234567890
remote:
remote: Diff:
remote: ---
remote:  a | 4 +++-
remote:  1 file changed, 3 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..a90d851 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,5 @@
remote:  Some file.
remote: -Second line.
remote: +Second line, in the middle.
remote: +In the middle too!
remote:  Third line.
remote: +
To ../bare/repo.git
   d065089..8f9e357  not-ok-104 -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
