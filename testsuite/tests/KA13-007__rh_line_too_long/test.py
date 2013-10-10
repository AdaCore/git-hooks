from support import *

class TestRun(TestCase):
    def test_push_commits(self):
        """See comments below.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push not-ok-104 on master. It introduces a new commit
        # where one line in the RH is 104 characters long.  It should
        # therefore be rejected.
        p = Run('git push origin not-ok-104:master'.split())
        expected_out = """\
remote: *** Invalid revision history for commit 8f9e357b53cc88eb0e7a57ee8c7d1ccd74db1ae3:
remote: ***
remote: *** The following line in the revision history is too long
remote: *** (104 characters, when the maximum is 76 characters):
remote: ***
remote: *** >>> 00000000011111111112222222222333333333344444444445555555555666666666677777777778888888888999999999900000
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] not-ok-104 -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push not-ok-77 on master. It introduces a new commit
        # where one line in the RH is 77 characters long, which
        # is just over the limit.  It should be rejected also.
        p = Run('git push origin not-ok-77:master'.split())
        expected_out = """\
remote: *** Invalid revision history for commit a80d278157a3a10c955360723b6520614f3c717c:
remote: ***
remote: *** The following line in the revision history is too long
remote: *** (77 characters, when the maximum is 76 characters):
remote: ***
remote: *** >>> 00000000011111111112222222222333333333344444444445555555555666666666677777777
remote: error: hook declined to update refs/heads/master
To ../bare/repo.git
 ! [remote rejected] not-ok-77 -> master (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push ok-76 on master. It introduces a new commit
        # where one line in the RH is 76 characters long, which
        # is just at the limit.  It should be accepted.
        p = Run('git push origin ok-76:master'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Updated a.
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: d065089ff184d97934c010ccd0e7e8ed94cb7165
remote: X-Git-Newrev: 04687d384d4a5cddb3f4ccc9dedb38c6582cb464
remote:
remote: commit 04687d384d4a5cddb3f4ccc9dedb38c6582cb464
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Apr 27 13:08:29 2012 -0700
remote:
remote:     Updated a.
remote:
remote:     Just added a little bit of text inside file a.
remote:     Thought about doing something else, but not really necessary.
remote:
remote:     0000000001111111111222222222233333333334444444444555555555566666666667777777
remote:     1234567890123456789012345678901234567890123456789012345678901234567890123456
remote:
remote: Diff:
remote: ---
remote:  a | 3 ++-
remote:  1 file changed, 2 insertions(+), 1 deletion(-)
remote:
remote: diff --git a/a b/a
remote: index 01d0f12..9caf4d6 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,3 +1,4 @@
remote:  Some file.
remote: -Second line.
remote: +Second line, in the middle.
remote:  Third line.
remote: +
To ../bare/repo.git
   d065089..04687d3  ok-76 -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push not-ok-77 on third-party. It introduces a new commit
        # where one line in the RH is 77 characters long, which is
        # just over the limit.  But the third-party branch is configured
        # with no-precommit-checks, so it should be accepted anyway.
        p = Run('git push origin not-ok-77:third-party'.split())
        expected_out = """\
remote: SYSLOG: cvs_check: Pre-commit checks disabled for a80d278157a3a10c955360723b6520614f3c717c on repo by hooks.no-precommit-check config (refs/heads/third-party)
remote: ----------------------------------------------------------------------
remote: --  The hooks.no-emails config option contains `refs/heads/third-party',
remote: --  which matches the name of the reference being updated
remote: --  (refs/heads/third-party).
remote: --
remote: --  Commit emails will therefore not be sent.
remote: ----------------------------------------------------------------------
To ../bare/repo.git
   d065089..a80d278  not-ok-77 -> third-party
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
