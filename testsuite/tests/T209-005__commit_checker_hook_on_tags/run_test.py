import os


def test_push_lightweight_tag(testcase):
    # In this testcase, the contents of the emails being sent
    # by the git-hooks is not important, so reduce verbosity at
    # that level to reduce the noise in the hooks' output.

    testcase.change_email_sending_verbosity(full_verbosity=False)

    # First, update the git-hooks configuration to install our
    # the script we want to use as our commit-extra-checker.

    testcase.update_git_hooks_config(
        [
            (
                "hooks.commit-extra-checker",
                os.path.join(testcase.work_dir, "commit-extra-checker.py"),
            ),
        ]
    )

    # Try pushing the lightweight tag light-tag. We expect the checker
    # to not be called at all, and the push to be succesful.
    #
    # Note that this tag points to a commit which would normally
    # trigger an error from the commit-extra-checker. However,
    # this commit has already been pushed to the remote, and thus
    # is not new, so the checker should not be called on it.
    p = testcase.run("git push origin light-tag".split())
    expected_out = """\
remote: DEBUG: Sending email: [repo] Created tag 'light-tag'...
To ../bare/repo.git
 * [new tag]         light-tag -> light-tag
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Try pushing the annotated tag annotated-tag-good. This new tag
    # points to commits which have already been pushed to the remote,
    # so there are no new commits being added besides this new tag.
    # As a result, the commit-extra-checker should not be called
    # at all.
    p = testcase.run("git push origin annotated-tag-good".split())
    expected_out = """\
remote: DEBUG: Sending email: [repo] Created tag 'annotated-tag-good'...
To ../bare/repo.git
 * [new tag]         annotated-tag-good -> annotated-tag-good
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Try pushing the annotated tag annotated-tag-new-commits-good.
    # This tag points to a couple of commits which have not been pushed
    # to the remove repository yet. As a result of that, we expect
    # the commit-extra-checker to be called for those commits.
    # The commits are expected to pass the checker, and so the push
    # is expected to succeed.

    p = testcase.run("git push origin annotated-tag-new-commits-good".split())
    expected_out = """\
remote: DEBUG: commit-extra-checker.py refs/tags/annotated-tag-new-commits-good 81792e975fbabb737876018499cb76123a2a599e
remote: -----[ stdin ]-----
remote:   . author_email: brobecker@adacore.com
remote:   . author_name: Joel Brobecker
remote:   . body: update a
remote:   . object_type: tag
remote:   . ref_kind: tag
remote:   . ref_name: refs/tags/annotated-tag-new-commits-good
remote:   . rev: 81792e975fbabb737876018499cb76123a2a599e
remote:   . subject: update a
remote: ---[ end stdin ]---
remote: DEBUG: commit-extra-checker.py refs/tags/annotated-tag-new-commits-good e3713ac0f17aea443e937dd38d0ef5f5fc360173
remote: -----[ stdin ]-----
remote:   . author_email: brobecker@adacore.com
remote:   . author_name: Joel Brobecker
remote:   . body: revert previous commit (unnecessary after all)
remote:   . object_type: tag
remote:   . ref_kind: tag
remote:   . ref_name: refs/tags/annotated-tag-new-commits-good
remote:   . rev: e3713ac0f17aea443e937dd38d0ef5f5fc360173
remote:   . subject: revert previous commit (unnecessary after all)
remote: ---[ end stdin ]---
remote: DEBUG: Sending email: [repo] Created tag 'annotated-tag-new-commits-good'...
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/annotated-tag-new-commits-good] update a...
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/annotated-tag-new-commits-good] revert previous commit (unnecessary after all)...
To ../bare/repo.git
 * [new tag]         annotated-tag-new-commits-good -> annotated-tag-new-commits-good
"""

    testcase.assertEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)

    # Try pushing the annotated tag annotated-tag-new-commits-bad.
    # This tag points to a couple of commits which have not been pushed
    # to the remove repository yet. As a result of that, we expect
    # the commit-extra-checker to be called for those commits.
    # The first commit has an (intentional) error which we expect
    # to trigger the commit-extra-checker, so the push is expected
    # to be rejected.

    p = testcase.run("git push origin annotated-tag-new-commits-bad".split())
    expected_out = """\
remote: *** The following commit was rejected by your hooks.commit-extra-checker script (status: 1)
remote: *** commit: 4be0bf1ff4ecc4a1f28641bba9dee46ae846a834
remote: *** DEBUG: commit-extra-checker.py refs/tags/annotated-tag-new-commits-bad 4be0bf1ff4ecc4a1f28641bba9dee46ae846a834
remote: *** -----[ stdin ]-----
remote: ***   . author_email: brobecker@adacore.com
remote: ***   . author_name: Joel Brobecker
remote: ***   . body: Update A to say "Now". This is bad form, hence (bad-commit)
remote: ***   . object_type: tag
remote: ***   . ref_kind: tag
remote: ***   . ref_name: refs/tags/annotated-tag-new-commits-bad
remote: ***   . rev: 4be0bf1ff4ecc4a1f28641bba9dee46ae846a834
remote: ***   . subject: Update A to say "Now". This is bad form, hence (bad-commit)
remote: *** ---[ end stdin ]---
remote: *** Error: Invalid bla bla bla. Rejecting Update.
remote: error: hook declined to update refs/tags/annotated-tag-new-commits-bad
To ../bare/repo.git
 ! [remote rejected] annotated-tag-new-commits-bad -> annotated-tag-new-commits-bad (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

    testcase.assertNotEqual(p.status, 0, p.image)
    testcase.assertRunOutputEqual(p, expected_out)
