import os


def test_push_commit_on_master(testcase):
    """Try pushing multiple commits on master."""
    # First, adjust the project.config file to use a commit-filer
    # script.  We have to do it manually here, because we need to
    # provide the full path to that script.
    with open("%s/hooks_config" % testcase.work_dir) as f:
        project_config = f.read() % {"TEST_DIR": testcase.work_dir}
    with open(os.path.join(testcase.repo_dir, "project.config"), "w") as f:
        f.write(project_config)
    p = testcase.run(["git", "commit", "-m", "fix hooks.mailinglist", "project.config"])
    assert p.status == 0, p.image

    p = testcase.run(
        ["git", "push", "origin", "refs/heads/meta/config:refs/meta/config"]
    )
    assert p.status == 0, p.image

    p = testcase.run("git checkout master".split())
    assert p.status == 0, p.image

    p = testcase.run("git push origin master".split())
    expected_out = """\
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
remote: -----[ post-receive-hook args ]-----
remote: -----[ post-receive-hook stdin ]-----
remote: 426fba3571947f6de7f967e885a3168b9df7004a dd6165c96db712d3e918fb5c61088b171b5e7cab refs/heads/master
remote: -----[ post-recieve-hook end ]-----
To ../bare/repo.git
   426fba3..dd6165c  master -> master
"""
    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
