from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing one single-file commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Push master to the `origin' remote.  The delta should be one
        # commit with one file being modified.
        p = Run('git push origin master'.split())
        expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Minor reformatting.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 937ea8ac48994bdef9928dc6e246bb1d3efb8acd
remote: X-Git-Newrev: 4b27b37bcd68460e2ec2ccd97a4e93660ed4cd16
remote:
remote: commit 4b27b37bcd68460e2ec2ccd97a4e93660ed4cd16
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Wed Jun 1 09:38:20 2016 -0700
remote:
remote:     Minor reformatting.
remote:
remote: Diff:
remote: ---
remote:  gms/hello.adb | 1 +
remote:  sec/README    | 3 +++
remote:  2 files changed, 4 insertions(+)
remote:
remote: diff --git a/gms/hello.adb b/gms/hello.adb
remote: index 9a6ff61..93db53d 100644
remote: --- a/gms/hello.adb
remote: +++ b/gms/hello.adb
remote: @@ -1,4 +1,5 @@
remote:  with Ada.Text_IO; use Ada.Text_IO;
remote: +
remote:  procedure Hello is
remote:  begin
remote:     Put_Line ("Hello World.");
remote: diff --git a/sec/README b/sec/README
remote: index a7e57ad..93f282d 100644
remote: --- a/sec/README
remote: +++ b/sec/README
remote: @@ -1 +1,4 @@
remote: +REPO's sec/ README:
remote: +-------------------
remote: +
remote:  This directory contains interesting stuff.
To ../bare/repo.git
   937ea8a..4b27b37  master -> master
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
