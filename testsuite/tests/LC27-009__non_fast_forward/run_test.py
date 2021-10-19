def test_push_commit_on_master(testcase):
    """Try non-fast-forward push on master."""
    p = testcase.run("git push -f origin master".split())
    expected_out = """\
remote: *** !!! WARNING: This is *NOT* a fast-forward update.
remote: *** !!! WARNING: You may have removed some important commits.
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Minor modifications.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote: X-Git-Newrev: 86c327680eae7942acad3d38e6503f3e05c338b0
remote:
remote: The branch 'master' was updated to point to:
remote:
remote:  86c3276... Minor modifications.
remote:
remote: It previously pointed to:
remote:
remote:  4f0f08f... Minor modifications.
remote:
remote: Diff:
remote:
remote: !!! WARNING: THE FOLLOWING COMMITS ARE NO LONGER ACCESSIBLE (LOST):
remote: -------------------------------------------------------------------
remote:
remote:   4f0f08f... Minor modifications.
remote:
remote:
remote: Summary of changes (added commits):
remote: -----------------------------------
remote:
remote:   86c3276... Minor modifications.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo] Minor modifications.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/master
remote: X-Git-Oldrev: 426fba3571947f6de7f967e885a3168b9df7004a
remote: X-Git-Newrev: 86c327680eae7942acad3d38e6503f3e05c338b0
remote:
remote: commit 86c327680eae7942acad3d38e6503f3e05c338b0
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Sat May 5 15:23:36 2012 -0700
remote:
remote:     Minor modifications.
remote:
remote: Diff:
remote: ---
remote:  a | 2 +-
remote:  c | 1 -
remote:  2 files changed, 1 insertion(+), 2 deletions(-)
remote:
remote: diff --git a/a b/a
remote: index 78822b6..0a89c71 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1,2 +1,2 @@
remote:  This is a file
remote: -with a second line.
remote: +with a 2nd line.
remote: diff --git a/c b/c
remote: index 4bc3eed..e0f1ee1 100644
remote: --- a/c
remote: +++ b/c
remote: @@ -1,2 +1 @@
remote:  hello world.
remote: -ZZ
To ../bare/repo.git
 + 4f0f08f...86c3276 master -> master (forced update)
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
