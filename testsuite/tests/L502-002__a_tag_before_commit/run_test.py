def test_push_commit_on_master(testcase):
    """Try pushing tag referencing new commit."""
    # We need some debug traces to be enabled, in order to verify
    # certain assertions.
    testcase.set_debug_level(1)

    # Scenario: The user made some changes, and then committed them
    # in his repo. Then created an annotated tag (release-0.1a).
    # Next, he pushes the annotated tag before having pushed his
    # new commit.  What the commit hooks should do in this case
    # is do the same as in a branch update (pre-commit checks,
    # commit emails, etc).

    p = testcase.run("git push origin version-0.1a".split())
    expected_out = """\
remote: DEBUG: validate_ref_update (refs/tags/version-0.1a, 0000000000000000000000000000000000000000, b03c3952e1cd29c6ec0cad2590689c0b22d02197)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: style_check_commit(old_rev=426fba3571947f6de7f967e885a3168b9df7004a, new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: *** cvs_check: `repo' < `a' `b' `c'
remote: DEBUG: post_receive_one(ref_name=refs/tags/version-0.1a
remote:                         old_rev=0000000000000000000000000000000000000000
remote:                         new_rev=b03c3952e1cd29c6ec0cad2590689c0b22d02197)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Created tag 'version-0.1a'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/tags/version-0.1a
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: b03c3952e1cd29c6ec0cad2590689c0b22d02197
remote:
remote: The unsigned tag 'version-0.1a' was created pointing to:
remote:
remote:  4f0f08f... Minor modifications.
remote:
remote: Tagger: Joel Brobecker <brobecker@adacore.com>
remote: Date: Fri May 11 15:56:32 2012 -0700
remote:
remote:     Tag version 0.1 alpha.
remote:
remote:     First (alpha) release of this project.
remote:
remote: Diff:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   4f0f08f... Minor modifications.
remote: DEBUG: inter-email delay...
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/version-0.1a] Minor modifications.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/tags/version-0.1a
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
To ../bare/repo.git
 * [new tag]         version-0.1a -> version-0.1a
"""

    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)

    # Next, push the changes.  The commits are no longer "new",
    # and thus nothing other than the reference change should
    # be done.

    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 426fba3571947f6de7f967e885a3168b9df7004a, 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=426fba3571947f6de7f967e885a3168b9df7004a
remote:                         new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
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
To ../bare/repo.git
   426fba3..4f0f08f  master -> master
"""

    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
