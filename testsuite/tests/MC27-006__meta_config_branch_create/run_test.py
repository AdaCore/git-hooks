from subprocess import check_output, check_call


def bare_repo_fixup(testcase):
    """Fix the bare repository to implement legacy hooks configuration.

    Reproduce the situation where the project.config file in
    refs/meta/config does not exist, yet.
    """
    check_call(
        "git update-ref -d refs/meta/config".split(),
        cwd=testcase.bare_repo_dir,
    )


def test_push_commit_on_master(testcase):
    """Test creating the refs/meta/config branch on the remote."""
    bare_repo_fixup(testcase)

    # Push the `meta/config' local branch as the new `refs/meta/config'
    # reference. This should be allowed.
    p = testcase.run("git push origin meta/config:refs/meta/config".split())
    expected_out = testcase.massage_git_output(
        """\
remote: *** cvs_check: `repo' < `project.config'
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'config' in namespace 'refs/meta'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: 7dcb1b7cb71d09ed70b3d64c8ddd993ec1d2d017
remote:
remote: The branch 'config' was created in namespace 'refs/meta' pointing to:
remote:
remote:  7dcb1b7... Initial config for project
remote: DEBUG: inter-email delay...
remote: DEBUG: MIME-Version: 1.0
remote: Content-Transfer-Encoding: 7bit
remote: Content-Type: text/plain; charset="utf-8"
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Bcc: filer@example.com
remote: Subject: [repo(refs/meta/config)] Initial config for project
remote: X-Act-Checkin: repo
remote: X-Git-Author: Joel Brobecker <brobecker@adacore.com>
remote: X-Git-Refname: refs/meta/config
remote: X-Git-Oldrev:
remote: X-Git-Newrev: 7dcb1b7cb71d09ed70b3d64c8ddd993ec1d2d017
remote:
remote: commit 7dcb1b7cb71d09ed70b3d64c8ddd993ec1d2d017
remote: Author: Joel Brobecker <brobecker@adacore.com>
remote: Date:   Fri Dec 27 15:32:11 2013 +0400
remote:
remote:     Initial config for project
remote:
remote: Diff:
remote: ---
remote:  project.config | 4 ++++
remote:  1 file changed, 4 insertions(+)
remote:
remote: diff --git a/project.config b/project.config
remote: new file mode 100644
remote: index 0000000..e565530
remote: --- /dev/null
remote: +++ b/project.config
remote: @@ -0,0 +1,4 @@
remote: +[hooks]
remote: +        from-domain = adacore.com
remote: +        mailinglist = git-hooks-ci@example.com
remote: +        filer-email = filer@example.com
To ../bare/repo.git
 * [new reference]   meta/config -> refs/meta/config
"""
    )

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
