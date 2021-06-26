from support import *

class TestRun(TestCase):
    def test_push_commit_on_master(self):
        """Try pushing commit on master.
        """
        cd ('%s/repo' % TEST_DIR)

        # Enable debug traces.  We use them to make certain verifications,
        # such as verifying that certain files are not being checked
        # because they are being deleted.
        self.set_debug_level(2)

        p = Run('git push origin master'.split())
        expected_out = """\
remote:   DEBUG: check_update(ref_name=refs/heads/master, old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42, new_rev=0c702ad3051f00b1251bca7a0241a3a9bf19bf0d)
remote: DEBUG: validate_ref_update (refs/heads/master, f82624871b6cfc46d5a7c5be518bc20e8f42be42, 0c702ad3051f00b1251bca7a0241a3a9bf19bf0d)
remote: DEBUG: update base: f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: style_check_commit(old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42, new_rev=0c702ad3051f00b1251bca7a0241a3a9bf19bf0d)
remote:   DEBUG: deleted file ignored: a.adb
remote:   DEBUG: deleted file ignored: b.adb
remote: DEBUG: style_check_commit: no files to style-check
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote:                         new_rev=0c702ad3051f00b1251bca7a0241a3a9bf19bf0d)
remote: DEBUG: update base: f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Remove all .adb files.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote: X-Git-Newrev: 0c702ad3051f00b1251bca7a0241a3a9bf19bf0d
remote:
remote: commit 0c702ad3051f00b1251bca7a0241a3a9bf19bf0d
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 16:05:13 2012 -0700
remote:
remote:     Remove all .adb files.
remote:
remote:     They need to be removed for our testing.
remote:
remote: Diff:
remote: ---
remote:  a.adb | 4 ----
remote:  b.adb | 4 ----
remote:  2 files changed, 8 deletions(-)
remote:
remote: diff --git a/a.adb b/a.adb
remote: deleted file mode 100644
remote: index be851a7..0000000
remote: --- a/a.adb
remote: +++ /dev/null
remote: @@ -1,4 +0,0 @@
remote: -procedure A is
remote: -begin
remote: -   null;
remote: -end A;
remote: diff --git a/b.adb b/b.adb
remote: deleted file mode 100644
remote: index fa77731..0000000
remote: --- a/b.adb
remote: +++ /dev/null
remote: @@ -1,4 +0,0 @@
remote: -function B (I : Integer) return Integer is
remote: -begin
remote: -   return 2 * I;
remote: -end B;
To ../bare/repo.git
   f826248..0c702ad  master -> master
"""
        assert p.status == 0, p.image
        self.assertRunOutputEqual(p, expected_out)

if __name__ == '__main__':
    runtests()
