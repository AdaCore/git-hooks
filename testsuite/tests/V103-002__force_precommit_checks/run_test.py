import os


def test_push_commits(testcase):
    """Try pushing multiple commits to various branches."""
    # We don't need to check the contents of the email, so turn
    # verbosity down.
    testcase.change_email_sending_verbosity(full_verbosity=False)

    # Enable debug traces.  We use them to make certain verifications,
    # such as verifying that each commit gets checked individually.
    testcase.set_debug_level(1)

    # First, update the git-hooks configuration to install
    # the script we want to use as our commit-extra-checker.

    testcase.update_git_hooks_config(
        [
            (
                "hooks.commit-extra-checker",
                os.path.join(testcase.work_dir, "commit-extra-checker.py"),
            ),
        ]
    )

    # Push master to master.
    #
    # The commits that are being pushed already exist in the remote
    # repository as part of another branch called feature-A.
    # So there should be no precommit checks being performed.

    p = testcase.run("git push origin master".split())
    expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/master, 426fba3571947f6de7f967e885a3168b9df7004a, dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: post_receive_one(ref_name=refs/heads/master
remote:                         old_rev=426fba3571947f6de7f967e885a3168b9df7004a
remote:                         new_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: Sending email: [repo] Minor modifications....
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo] 1 modified file, 1 new file....
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo] Modify `c', delete `b'....
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo] Modify file `d' alone....
To ../bare/repo.git
   426fba3..dd6165c  master -> master
"""
    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)

    # Do the same, but this time pushing to a branch called always-checked,
    # which is configured to always have pre-commit-checks.
    #
    # It's the same update as the master branch update just above, except
    # that this time we expect precommit checks to run for all new commits.

    p = testcase.run("git push origin master:always-checked".split())
    expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/always-checked, 426fba3571947f6de7f967e885a3168b9df7004a, dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: commit-extra-checker.py refs/heads/always-checked 4f0f08f46daf6f5455cf90cdc427443fe3b32fa3
remote: DEBUG: commit-extra-checker.py refs/heads/always-checked 4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf
remote: DEBUG: commit-extra-checker.py refs/heads/always-checked cc8d2c2637bda27f0bc2125181dd2f8534d16222
remote: DEBUG: commit-extra-checker.py refs/heads/always-checked dd6165c96db712d3e918fb5c61088b171b5e7cab
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: style_check_commit(old_rev=426fba3571947f6de7f967e885a3168b9df7004a, new_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3)
remote: *** cvs_check: `repo' < `a' `b' `c'
remote: DEBUG: style_check_commit(old_rev=4f0f08f46daf6f5455cf90cdc427443fe3b32fa3, new_rev=4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf)
remote: *** cvs_check: `repo' < `c' `d'
remote: DEBUG: style_check_commit(old_rev=4a325b31f594b1dc2c66ac15c4b6b68702bd0cdf, new_rev=cc8d2c2637bda27f0bc2125181dd2f8534d16222)
remote: *** cvs_check: `repo' < `c'
remote: DEBUG: style_check_commit(old_rev=cc8d2c2637bda27f0bc2125181dd2f8534d16222, new_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: *** cvs_check: `repo' < `d'
remote: DEBUG: post_receive_one(ref_name=refs/heads/always-checked
remote:                         old_rev=426fba3571947f6de7f967e885a3168b9df7004a
remote:                         new_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab)
remote: DEBUG: update base: 426fba3571947f6de7f967e885a3168b9df7004a
remote: DEBUG: Sending email: [repo/always-checked] Minor modifications....
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/always-checked] 1 modified file, 1 new file....
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/always-checked] Modify `c', delete `b'....
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/always-checked] Modify file `d' alone....
To ../bare/repo.git
   426fba3..dd6165c  master -> always-checked
"""
    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)

    # Create a new branch whose name also matches the project's
    # force-precommit-checks.
    #
    # In this case, we only expect the precommit checks for commits
    # which are entirely new (the branch is equivalent to master
    # plus another branch new commit). Therefore, we should get
    # precommit-check for that brand new commit, and that's it.

    p = testcase.run("git push origin always-checked-new".split())
    expected_out = """\
remote: DEBUG: validate_ref_update (refs/heads/always-checked-new, 0000000000000000000000000000000000000000, f33e91d6c4eda87490ce07920d4f8886f3dcb2b2)
remote: DEBUG: update base: dd6165c96db712d3e918fb5c61088b171b5e7cab
remote: DEBUG: commit-extra-checker.py refs/heads/always-checked-new f33e91d6c4eda87490ce07920d4f8886f3dcb2b2
remote: DEBUG: (commit-per-commit style checking)
remote: DEBUG: style_check_commit(old_rev=dd6165c96db712d3e918fb5c61088b171b5e7cab, new_rev=f33e91d6c4eda87490ce07920d4f8886f3dcb2b2)
remote: *** cvs_check: `repo' < `d'
remote: DEBUG: post_receive_one(ref_name=refs/heads/always-checked-new
remote:                         old_rev=0000000000000000000000000000000000000000
remote:                         new_rev=f33e91d6c4eda87490ce07920d4f8886f3dcb2b2)
remote: DEBUG: update base: dd6165c96db712d3e918fb5c61088b171b5e7cab
remote: DEBUG: Sending email: [repo] Created branch 'always-checked-new'...
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/always-checked-new] update `d' to give more information about its contents...
To ../bare/repo.git
 * [new branch]      always-checked-new -> always-checked-new
"""
    assert p.status == 0, p.image
    testcase.assertRunOutputEqual(p, expected_out)
