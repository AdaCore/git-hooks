def test_push_commit_on_master(testcase):
    """Try pushing new branch on remote.

    In this situation, release-0.1-branch points to the same
    commit as the master branch.
    """
    p = testcase.run("git push origin release-0.1-branch".split())
    expected_out = """\
remote: DEBUG: Content-Type: text/plain; charset="utf-8"
remote: MIME-Version: 1.0
remote: Content-Transfer-Encoding: quoted-printable
remote: From: Test Suite <testsuite@adacore.com>
remote: To: git-hooks-ci@example.com
remote: Subject: [repo] Created branch 'release-0.1-branch'
remote: X-Act-Checkin: repo
remote: X-Git-Author: Test Suite <testsuite@adacore.com>
remote: X-Git-Refname: refs/heads/release-0.1-branch
remote: X-Git-Oldrev: 0000000000000000000000000000000000000000
remote: X-Git-Newrev: dd6165c96db712d3e918fb5c61088b171b5e7cab
remote:
remote: The branch 'release-0.1-branch' was created pointing to:
remote:
remote:  dd6165c... Modify file `d' alone.
To ../bare/repo.git
 * [new branch]      release-0.1-branch -> release-0.1-branch
"""

    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)

    # Verify that the branch has been created in the remote
    # repository and that it points to the expected commit.

    p = testcase.run(
        "git show-ref -s release-0.1-branch".split(), cwd=testcase.bare_repo_dir
    )
    expected_out = """\
dd6165c96db712d3e918fb5c61088b171b5e7cab
"""

    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
