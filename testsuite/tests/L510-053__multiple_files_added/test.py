from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        p = Run('git push origin master'.split())
        expected_out = """\
remote: *** cvs_check: `repo' < `pck.adb' `pck.ads' `types.ads'
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Add 3 files.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote: X-Git-Newrev: c699b49d82d8c18c519f41dacb78839fc7416edb
remote:
remote: commit c699b49d82d8c18c519f41dacb78839fc7416edb
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 16:48:33 2012 -0700
remote:
remote:     Add 3 files.
remote:
remote: Diff:
remote: ---
remote:  pck.adb   | 6 ++++++
remote:  pck.ads   | 4 ++++
remote:  types.ads | 3 +++
remote:  3 files changed, 13 insertions(+)
remote:
remote: diff --git a/pck.adb b/pck.adb
remote: new file mode 100644
remote: index 0000000..597c010
remote: --- /dev/null
remote: +++ b/pck.adb
remote: @@ -0,0 +1,6 @@
remote: +package body Pck is
remote: +   procedure Do_Nothing is
remote: +   begin
remote: +      null;
remote: +   end Do_Nothing;
remote: +end Pck;
remote: diff --git a/pck.ads b/pck.ads
remote: new file mode 100644
remote: index 0000000..48d49ce
remote: --- /dev/null
remote: +++ b/pck.ads
remote: @@ -0,0 +1,4 @@
remote: +package Pck is
remote: +   Something : Integer := 15;
remote: +   procedure Do_Nothing;
remote: +end Pck;
remote: diff --git a/types.ads b/types.ads
remote: new file mode 100644
remote: index 0000000..183f19d
remote: --- /dev/null
remote: +++ b/types.ads
remote: @@ -0,0 +1,3 @@
remote: +package Types is
remote: +   type Small is mod 0 .. 2 ** 8 - 1;
remote: +end Types;
To ../bare/repo.git
   f826248..c699b49  master -> master
"""

        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
