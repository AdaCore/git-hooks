from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing multiple commits on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that each commit gets checked individually.
        self.set_debug_level(2)

        p = Run('git push origin master'.split())
        expected_out = """\
remote:   DEBUG: check_update(ref_name=refs/heads/master, old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42, new_rev=adb8ffe7b1718f6f8a6ec22f7c0ff06b83f086ec)
remote: DEBUG: validate_ref_update (refs/heads/master, f82624871b6cfc46d5a7c5be518bc20e8f42be42, adb8ffe7b1718f6f8a6ec22f7c0ff06b83f086ec)
remote: DEBUG: update base: f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: check_commit(old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42, new_rev=adb8ffe7b1718f6f8a6ec22f7c0ff06b83f086ec)
remote:   DEBUG: deleted file ignored: foo.c
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote:                         new_rev=adb8ffe7b1718f6f8a6ec22f7c0ff06b83f086ec)
remote: DEBUG: update base: f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote: DEBUG: Content-Type: text/plain; charset="us-ascii"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: file-ci@gnat.com
remote: Subject: [repo] Delete foo.c
remote: X-Act-Checkin: repo
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote: X-Git-Newrev: adb8ffe7b1718f6f8a6ec22f7c0ff06b83f086ec
remote:
remote: commit adb8ffe7b1718f6f8a6ec22f7c0ff06b83f086ec
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 15:56:29 2012 -0700
remote:
remote:     Delete foo.c
remote:
remote:     Some explanations of why that is.
remote:
remote: Diff:
remote: ---
remote:  foo.c |    4 ----
remote:  1 file changed, 4 deletions(-)
remote:
remote: diff --git a/foo.c b/foo.c
remote: deleted file mode 100644
remote: index f5b1c50..0000000
remote: --- a/foo.c
remote: +++ /dev/null
remote: @@ -1,4 +0,0 @@
remote: -#include <stdlib.h>
remote: -
remote: -void *global_var = NULL;
remote: -
To ../bare/repo.git
   f826248..adb8ffe  master -> master
"""
        self.assertTrue(p.status == 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
