import os


def test_push_commit_on_master(testcase):
    """Try pushing multiple commits on master."""
    # Enable debug traces.  We use them to make certain verifications,
    # such as verifying that each commit gets checked individually.
    testcase.set_debug_level(1)

    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 426fba3571947f6de7f967e885a3168b9df7004a, dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: style_check_commit(old_rev=426fba3571947f6de7f967e885a3168b9df7004a, new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: *** cvs_check: `repo' < `a' `b' `c'
remote: DEBUG: style_check_commit(old_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3, new_rev=4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf)
remote: *** cvs_check: `repo' < `c' `d'
remote: DEBUG: style_check_commit(old_rev=4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf, new_rev=cc8d2c2637bda27f0bc2125181dd2f8534d16222)
remote: *** cvs_check: `repo' < `c'
remote: DEBUG: style_check_commit(old_rev=cc8d2c2637bda27f0bc2125181dd2f8534d16222, new_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: *** cvs_check: `repo' < `d'
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=426fba3571947f6de7f967e885a3168b9df7004a
remote:                         new_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com, user@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Minor modifications.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 426fba3571947f6de7f967e885a3168b9df7004a
remote: X-Git-Newrev: 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote:
remote: commit 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat May 5 15:23:36 2012 -0700
remote:
remote:     Minor modifications.
remote:
remote: Diff:
remote: ---
remote:  a | 2 +-
remote:  b | 2 +-
remote:  c | 1 -
remote:  3 files changed, 2 insertions(+), 3 deletions(-)
remote:
remote: diff --git a/a b/a
remote: index 78822b6..0a89c71 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,2 +1,2 @@
remote:  This is a file
remote: -with a second line.
remote: +with a 2nd line.
remote: diff --git a/b b/b
remote: index 373ad20..6ac1308 100644
remote: --- a/b
remote: +++ b/b
remote: @@ -1,3 +1,3 @@
remote:  some contents inside
remote:  that file
remote: -that isn't really all that interesting.
remote: +that is not really all that interesting.
remote: diff --git a/c b/c
remote: index 4bc3eed..e0f1ee1 100644
remote: --- a/c
remote: +++ b/c
remote: @@ -1,2 +1 @@
remote:  hello world.
remote: -ZZ
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com, user@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] 1 modified file, 1 new file.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote: X-Git-Newrev: 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
remote:
remote: commit 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 15:20:05 2012 -0700
remote:
remote:     1 modified file, 1 new file.
remote:
remote: Diff:
remote: ---
remote:  c | 1 +
remote:  d | 1 +
remote:  2 files changed, 2 insertions(+)
remote:
remote: diff --git a/c b/c
remote: index e0f1ee1..11ba4d0 100644
remote: --- a/c
remote: +++ b/c
remote: @@ -1 +1,2 @@
remote:  hello world.
remote: +This is file number C.
remote: diff --git a/d b/d
remote: new file mode 100644
remote: index 0000000..6434b13
remote: --- /dev/null
remote: +++ b/d
remote: @@ -0,0 +1 @@
remote: +This is a new file.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com, user@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Modify `c', delete `b'.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
remote: X-Git-Newrev: cc8d2c2637bda27f0bc2125181dd2f8534d16222
remote:
remote: commit cc8d2c2637bda27f0bc2125181dd2f8534d16222
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 15:21:06 2012 -0700
remote:
remote:     Modify `c', delete `b'.
remote:
remote: Diff:
remote: ---
remote:  b | 3 ---
remote:  c | 2 +-
remote:  2 files changed, 1 insertion(+), 4 deletions(-)
remote:
remote: diff --git a/b b/b
remote: deleted file mode 100644
remote: index 6ac1308..0000000
remote: --- a/b
remote: +++ /dev/null
remote: @@ -1,3 +0,0 @@
remote: -some contents inside
remote: -that file
remote: -that is not really all that interesting.
remote: diff --git a/c b/c
remote: index 11ba4d0..ef3fe05 100644
remote: --- a/c
remote: +++ b/c
remote: @@ -1,2 +1,2 @@
remote:  hello world.
remote: -This is file number C.
remote: +This is file number c.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com, user@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Modify file `d' alone.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: cc8d2c2637bda27f0bc2125181dd2f8534d16222
remote: X-Git-Newrev: dd6165c96db712d3e918fb5c61088b171b5e7cab
remote:
remote: commit dd6165c96db712d3e918fb5c61088b171b5e7cab
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Thu May 10 15:21:57 2012 -0700
remote:
remote:     Modify file `d' alone.
remote:
remote: Diff:
remote: ---
remote:  d | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/d b/d
remote: index 6434b13..2def2d6 100644
remote: --- a/d
remote: +++ b/d
remote: @@ -1 +1,2 @@
remote: +Title: D
remote:  This is a new file.
To ../bare/repo.git
   426fba3..dd6165c  master -> master
"""
    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)

    # Add testing of manual commit email resending (for UC02-038).
    #
    # For that, we simulate user going into the bare repository,
    # and calling the post-receive hook with the correct parameters
    # for resending the emails from the push above.

    testcase.set_debug_level(0)

    resending_environ = {
        "GIT_HOOKS_EMAIL_REPLAY_REASON": "TICK-ET#",
    }

    sha1_before = "426fba3571947f6de7f967e885a3168b9df7004a"
    sha1_after = "dd6165c96db712d3e918fb5c61088b171b5e7cab"
    ref_name = "refs/heads/master"

    p = testcase.run(
        [os.path.join(testcase.bare_repo_dir, "hooks", "post-receive")],
        input=f"|{sha1_before} {sha1_after} {ref_name}",
        cwd=testcase.bare_repo_dir,
        env=resending_environ,
    )

    expected_out = """\
DEBUG: Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: quoted-printable
From: Test Suite <testsuite@adacore.com>
To: git-hooks-ci@example.com, user@example.com
Bcc: filer@example.com
Subject: [repo] Minor modifications.
X-Act-Checkin: repo
X-Git-Author: Joel Brobecker <brobecker@adacore.com>
X-Git-Refname: refs/heads/master
X-Git-Oldrev: 426fba3571947f6de7f967e885a3168b9df7004a
X-Git-Newrev: 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3

======================================================================
==  WARNING: THIS EMAIL WAS MANUALLY RE-SENT (TICK-ET#)]
==
==  The email's date is therefore NOT representative of when
==  the corresponding update was actually pushed to the repository.
======================================================================

commit 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
Author: Joel Brobecker <brobecker@adacore.com>
Date:   Sat May 5 15:23:36 2012 -0700

    Minor modifications.

Diff:
---
 a | 2 +-
 b | 2 +-
 c | 1 -
 3 files changed, 2 insertions(+), 3 deletions(-)

diff --git a/a b/a
index 78822b6..0a89c71 100644
--- a/a
+++ b/a
@@ -1,2 +1,2 @@
 This is a file
-with a second line.
+with a 2nd line.
diff --git a/b b/b
index 373ad20..6ac1308 100644
--- a/b
+++ b/b
@@ -1,3 +1,3 @@
 some contents inside
 that file
-that isn't really all that interesting.
+that is not really all that interesting.
diff --git a/c b/c
index 4bc3eed..e0f1ee1 100644
--- a/c
+++ b/c
@@ -1,2 +1 @@
 hello world.
-ZZ
DEBUG: inter-email delay...
DEBUG: Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: quoted-printable
From: Test Suite <testsuite@adacore.com>
To: git-hooks-ci@example.com, user@example.com
Bcc: filer@example.com
Subject: [repo] 1 modified file, 1 new file.
X-Act-Checkin: repo
X-Git-Author: Joel Brobecker <brobecker@adacore.com>
X-Git-Refname: refs/heads/master
X-Git-Oldrev: 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
X-Git-Newrev: 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf

======================================================================
==  WARNING: THIS EMAIL WAS MANUALLY RE-SENT (TICK-ET#)]
==
==  The email's date is therefore NOT representative of when
==  the corresponding update was actually pushed to the repository.
======================================================================

commit 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
Author: Joel Brobecker <brobecker@adacore.com>
Date:   Thu May 10 15:20:05 2012 -0700

    1 modified file, 1 new file.

Diff:
---
 c | 1 +
 d | 1 +
 2 files changed, 2 insertions(+)

diff --git a/c b/c
index e0f1ee1..11ba4d0 100644
--- a/c
+++ b/c
@@ -1 +1,2 @@
 hello world.
+This is file number C.
diff --git a/d b/d
new file mode 100644
index 0000000..6434b13
--- /dev/null
+++ b/d
@@ -0,0 +1 @@
+This is a new file.
DEBUG: inter-email delay...
DEBUG: Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: quoted-printable
From: Test Suite <testsuite@adacore.com>
To: git-hooks-ci@example.com, user@example.com
Bcc: filer@example.com
Subject: [repo] Modify `c', delete `b'.
X-Act-Checkin: repo
X-Git-Author: Joel Brobecker <brobecker@adacore.com>
X-Git-Refname: refs/heads/master
X-Git-Oldrev: 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
X-Git-Newrev: cc8d2c2637bda27f0bc2125181dd2f8534d16222

======================================================================
==  WARNING: THIS EMAIL WAS MANUALLY RE-SENT (TICK-ET#)]
==
==  The email's date is therefore NOT representative of when
==  the corresponding update was actually pushed to the repository.
======================================================================

commit cc8d2c2637bda27f0bc2125181dd2f8534d16222
Author: Joel Brobecker <brobecker@adacore.com>
Date:   Thu May 10 15:21:06 2012 -0700

    Modify `c', delete `b'.

Diff:
---
 b | 3 ---
 c | 2 +-
 2 files changed, 1 insertion(+), 4 deletions(-)

diff --git a/b b/b
deleted file mode 100644
index 6ac1308..0000000
--- a/b
+++ /dev/null
@@ -1,3 +0,0 @@
-some contents inside
-that file
-that is not really all that interesting.
diff --git a/c b/c
index 11ba4d0..ef3fe05 100644
--- a/c
+++ b/c
@@ -1,2 +1,2 @@
 hello world.
-This is file number C.
+This is file number c.
DEBUG: inter-email delay...
DEBUG: Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: quoted-printable
From: Test Suite <testsuite@adacore.com>
To: git-hooks-ci@example.com, user@example.com
Bcc: filer@example.com
Subject: [repo] Modify file `d' alone.
X-Act-Checkin: repo
X-Git-Author: Joel Brobecker <brobecker@adacore.com>
X-Git-Refname: refs/heads/master
X-Git-Oldrev: cc8d2c2637bda27f0bc2125181dd2f8534d16222
X-Git-Newrev: dd6165c96db712d3e918fb5c61088b171b5e7cab

======================================================================
==  WARNING: THIS EMAIL WAS MANUALLY RE-SENT (TICK-ET#)]
==
==  The email's date is therefore NOT representative of when
==  the corresponding update was actually pushed to the repository.
======================================================================

commit dd6165c96db712d3e918fb5c61088b171b5e7cab
Author: Joel Brobecker <brobecker@adacore.com>
Date:   Thu May 10 15:21:57 2012 -0700

    Modify file `d' alone.

Diff:
---
 d | 1 +
 1 file changed, 1 insertion(+)

diff --git a/d b/d
index 6434b13..2def2d6 100644
--- a/d
+++ b/d
@@ -1 +1,2 @@
+Title: D
 This is a new file.
"""
    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
