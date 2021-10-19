def test_push_github_pull_19(testcase):
    """Try pushing the branch named "github/pull/19" """
    # This branch contains a .gitreview whose defaultbranch setting
    # points to another branch name. So normally, the hooks should
    # reject this update, asking for the config to be changed instead.
    # However, the repository has been configured to allow updates
    # for branches whose name start with "github/pull/", so we expect
    # the push to be accepted.

    p = testcase.run("git push origin github/pull/19".split())
    expected_out = """\
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'github/pull/19'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/github/pull/19
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 863805de6bc5967f9aa2686d1f59c553cf81cf49
remote:
remote: The branch 'github/pull/19' was created pointing to:
remote:
remote:  863805d... Update a.
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo/github/pull/19] Update a.
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/heads/github/pull/19
remote: X-Git-Oldrev: 16d76a092abc9e4a314e5da67d3111f3bb11a56a
remote: X-Git-Newrev: 863805de6bc5967f9aa2686d1f59c553cf81cf49
remote:
remote: commit 863805de6bc5967f9aa2686d1f59c553cf81cf49
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Jul 28 14:32:32 2017 -0700
remote:
remote:     Update a.
remote:
remote: Diff:
remote: ---
remote:  a | 1 +
remote:  1 file changed, 1 insertion(+)
remote:
remote: diff --git a/a b/a
remote: index bf84ca6..22715c0 100644
remote: --- a/a
remote: +++ b/a
remote: @@ -1 +1,2 @@
remote:  Some file.
remote: +----------
To ../bare/repo.git
 * [new branch]      github/pull/19 -> github/pull/19
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
