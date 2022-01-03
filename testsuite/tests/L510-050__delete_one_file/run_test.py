def test_push_commit_on_master(testcase):
    """Try pushing multiple commits on master."""
    # Enable debug traces.  We use them to make certain verifications,
    # such as verifying that each commit gets checked individually.
    testcase.set_debug_level(2)

    p = testcase.run("git push origin master".split())
    expected_out = """\
remote:   DEBUG: check_update(ref_name=refs/heads/master, old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42, new_rev=adb8ffe7b1718f6f8a6ec22f7c0ff06b83f086ec)
remote: DEBUG: validate_ref_update (refs/heads/master, f82624871b6cfc46d5a7c5be518bc20e8f42be42, adb8ffe7b1718f6f8a6ec22f7c0ff06b83f086ec)
remote: DEBUG: update base: f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: style_check_commit(old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42, new_rev=adb8ffe7b1718f6f8a6ec22f7c0ff06b83f086ec)
remote:   DEBUG: deleted file ignored: foo.c
remote: DEBUG: style_check_commit: no files to style-check
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote:                         new_rev=adb8ffe7b1718f6f8a6ec22f7c0ff06b83f086ec)
remote: DEBUG: update base: f82624871b6cfc46d5a7c5be518bc20e8f42be42
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Delete foo.c
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
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
remote:  foo.c | 4 ----
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
    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
