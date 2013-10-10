from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** cvs_check: `trunk/repo/pck.ads'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Add single file pck.ads.
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote: X-Git-Newrev: 52f1517edfdd0a74916f010f1a95997113639749
remote:
remote: commit 52f1517edfdd0a74916f010f1a95997113639749
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 16:39:29 2012 -0700
remote:
remote:     Add single file pck.ads.
remote:
remote: Diff:
remote: ---
remote:  pck.ads | 3 +++
remote:  1 file changed, 3 insertions(+)
remote:
remote: diff --git a/pck.ads b/pck.ads
remote: new file mode 100644
remote: index 0000000..1ec332f
remote: --- /dev/null
remote: +++ b/pck.ads
remote: @@ -0,0 +1,3 @@
remote: +package Pck is
remote: +   Something : Integer := 15;
remote: +end Pck;
To ../bare/repo.git
   f826248..52f1517  master -> master
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
