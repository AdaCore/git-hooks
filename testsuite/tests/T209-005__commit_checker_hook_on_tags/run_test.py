from support import *

class TestRun(TestCase):
    def test_push_lightweight_tag(self):
        cd ('%s/repo' % TEST_DIR)

        # In this testcase, the contents of the emails being sent
        # by the git-hooks is not important, so reduce verbosity at
        # that level to reduce the noise in the hooks' output.

        self.change_email_sending_verbosity(full_verbosity=False)

        # First, update the git-hooks configuration to install our
        # the script we want to use as our commit-extra-checker.

        p = Run(['git', 'fetch', 'origin', 'refs/meta/config'])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'checkout', 'FETCH_HEAD'])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'config', '--file', 'project.config',
                 'hooks.commit-extra-checker',
                 os.path.join(TEST_DIR, 'commit-extra-checker.py')])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'commit', '-m', 'Add hooks.commit-extra-checker',
                 'project.config'])
        self.assertEqual(p.status, 0, p.image)

        p = Run(['git', 'push', 'origin', 'HEAD:refs/meta/config'])
        self.assertEqual(p.status, 0, p.image)
        # Check the last line that git printed, and verify that we have
        # another piece of evidence that the change was succesfully pushed.
        self.assertTrue('HEAD -> refs/meta/config' in p.out.splitlines()[-1],
                        p.image)

        # Try pushing the lightweight tag light-tag. We expect the checker
        # to not be called at all, and the push to be succesful.
        #
        # Note that this tag points to a commit which would normally
        # trigger an error from the commit-extra-checker. However,
        # this commit has already been pushed to the remote, and thus
        # is not new, so the checker should not be called on it.
        p = Run('git push origin light-tag'.split())
        expected_out = """\
remote: DEBUG: Sending email: [repo] Created tag 'light-tag'...
To ../bare/repo.git
 * [new tag]         light-tag -> light-tag
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Try pushing the annotated tag annotated-tag-good. This new tag
        # points to commits which have already been pushed to the remote,
        # so there are no new commits being added besides this new tag.
        # As a result, the commit-extra-checker should not be called
        # at all.
        p = Run('git push origin annotated-tag-good'.split())
        expected_out = """\
remote: DEBUG: Sending email: [repo] Created tag 'annotated-tag-good'...
To ../bare/repo.git
 * [new tag]         annotated-tag-good -> annotated-tag-good
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Try pushing the annotated tag annotated-tag-new-commits-good.
        # This tag points to a couple of commits which have not been pushed
        # to the remove repository yet. As a result of that, we expect
        # the commit-extra-checker to be called for those commits.
        # The commits are expected to pass the checker, and so the push
        # is expected to succeed.

        p = Run('git push origin annotated-tag-new-commits-good'.split())
        expected_out = """\
remote: DEBUG: commit-extra-checker.py refs/tags/annotated-tag-new-commits-good 81792e975fbabb737876018499cb76123a2a599e
remote: -----[ stdin ]-----
remote: {"ref_kind": "tag", "body": "update a", "author_email": "brobecker@adacore.com", "subject": "update a", "object_type": "tag", "rev": "81792e975fbabb737876018499cb76123a2a599e", "author_name": "Joel Brobecker", "ref_name": "refs/tags/annotated-tag-new-commits-good"}
remote: ---[ end stdin ]---
remote: DEBUG: commit-extra-checker.py refs/tags/annotated-tag-new-commits-good e3713ac0f17aea443e937dd38d0ef5f5fc360173
remote: -----[ stdin ]-----
remote: {"ref_kind": "tag", "body": "revert previous commit (unnecessary after all)", "author_email": "brobecker@adacore.com", "subject": "revert previous commit (unnecessary after all)", "object_type": "tag", "rev": "e3713ac0f17aea443e937dd38d0ef5f5fc360173", "author_name": "Joel Brobecker", "ref_name": "refs/tags/annotated-tag-new-commits-good"}
remote: ---[ end stdin ]---
remote: DEBUG: Sending email: [repo] Created tag 'annotated-tag-new-commits-good'...
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/annotated-tag-new-commits-good] update a...
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/annotated-tag-new-commits-good] revert previous commit (unnecessary after all)...
To ../bare/repo.git
 * [new tag]         annotated-tag-new-commits-good -> annotated-tag-new-commits-good
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Try pushing the annotated tag annotated-tag-new-commits-bad.
        # This tag points to a couple of commits which have not been pushed
        # to the remove repository yet. As a result of that, we expect
        # the commit-extra-checker to be called for those commits.
        # The first commit has an (intentional) error which we expect
        # to trigger the commit-extra-checker, so the push is expected
        # to be rejected.

        p = Run('git push origin annotated-tag-new-commits-bad'.split())
        expected_out = """\
remote: *** The following commit was rejected by your hooks.commit-extra-checker script (status: 1)
remote: *** commit: 4be0bf1ff4ecc4a1f28641bba9dee46ae846a834
remote: *** DEBUG: commit-extra-checker.py refs/tags/annotated-tag-new-commits-bad 4be0bf1ff4ecc4a1f28641bba9dee46ae846a834
remote: *** -----[ stdin ]-----
remote: *** {"ref_kind": "tag", "body": "Update A to say \\"Now\\". This is bad form, hence (bad-commit)", "author_email": "brobecker@adacore.com", "subject": "Update A to say \\"Now\\". This is bad form, hence (bad-commit)", "object_type": "tag", "rev": "4be0bf1ff4ecc4a1f28641bba9dee46ae846a834", "author_name": "Joel Brobecker", "ref_name": "refs/tags/annotated-tag-new-commits-bad"}
remote: *** ---[ end stdin ]---
remote: *** Error: Invalid bla bla bla. Rejecting Update.
remote: error: hook declined to update refs/tags/annotated-tag-new-commits-bad
To ../bare/repo.git
 ! [remote rejected] annotated-tag-new-commits-bad -> annotated-tag-new-commits-bad (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
