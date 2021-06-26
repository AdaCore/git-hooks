import os
from support import cd, Run, runtests, TestCase, TEST_DIR

class TestRun(TestCase):
    def test_commit_checker_hook_on_branches(self):
        """Test pushing branch updates with a commit-extra-checker.

        The purpose of this testcase is to perform a sanity-check
        of the various branch push scenarios for repositories whose
        git-hooks configuration define hooks.commit-extra-checker.
        The main objective is to verify that this hook is called
        when expected, and only when expected, and that the hooks
        handle its return value correctly.

        The script we use for that is called commit-extra-checker.py,
        and was written to facilitate...
          - verification: It simply dumps on standard output the scripts
            arguments and data passed via stdin;
          - testing: It passes all commits unless it finds the string
            "(bad-commit)" somewhere in the stdin data given. That way,
            for commits we want the script to reject, we add that string
            to the commit's revision log.
        """
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

        # While at it, verify that the commit-extra-checker was called
        # to check that commit. Our hooks generates some output so
        # look for that.
        assert 'DEBUG: commit-extra-checker.py' in p.out, p.image

        # Push a branch which introduces a single new commit, which
        # we expect the commit-extra-checker to accept the commit.

        p = Run('git push origin single-commit-accept'.split())
        expected_out = """\
remote: DEBUG: commit-extra-checker.py refs/heads/single-commit-accept f109361240e74d710e8e7927495104ab40943060
remote: -----[ stdin ]-----
remote: {"ref_kind": "branch", "body": "This is an ok commit touching file a.", "author_email": "brobecker@adacore.com", "subject": "This is an ok commit touching file a.", "object_type": "commit", "rev": "f109361240e74d710e8e7927495104ab40943060", "author_name": "Joel Brobecker", "ref_name": "refs/heads/single-commit-accept"}
remote: ---[ end stdin ]---
remote: DEBUG: Sending email: [repo/single-commit-accept] This is an ok commit touching file a....
To ../bare/repo.git
   1e1e706..f109361  single-commit-accept -> single-commit-accept
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push a branch which introduces a single new commit,
        # which we expect the commit-extra-checker to reject.

        p = Run('git push origin single-commit-reject'.split())
        expected_out = """\
remote: *** The following commit was rejected by your hooks.commit-extra-checker script (status: 1)
remote: *** commit: 2c27994b8413d8b9515ebd38a0b229639809e5c1
remote: *** DEBUG: commit-extra-checker.py refs/heads/single-commit-reject 2c27994b8413d8b9515ebd38a0b229639809e5c1
remote: *** -----[ stdin ]-----
remote: *** {"ref_kind": "branch", "body": "modify a with some contents (bad-commit)", "author_email": "brobecker@adacore.com", "subject": "modify a with some contents (bad-commit)", "object_type": "commit", "rev": "2c27994b8413d8b9515ebd38a0b229639809e5c1", "author_name": "Joel Brobecker", "ref_name": "refs/heads/single-commit-reject"}
remote: *** ---[ end stdin ]---
remote: *** Error: Invalid bla bla bla. Rejecting Update.
remote: error: hook declined to update refs/heads/single-commit-reject
To ../bare/repo.git
 ! [remote rejected] single-commit-reject -> single-commit-reject (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push a branch which introduces more than one new commit,
        # which we expect the commit-extra-checker to accept.
        #
        # This push updates the branch with 3 new commits, and the 3 commits
        # are completely new for the repository, meaning that the commits
        # haven't already been pushed via other branches. As a result of
        # these commits being completely new, the commit-extra-checker
        # is expected to be called for each and every of these 3 commits.

        p = Run('git push origin multiple-commits-accept-all-new'.split())
        expected_out = """\
remote: DEBUG: commit-extra-checker.py refs/heads/multiple-commits-accept-all-new 4a250d3fd87947c594579e14b5688d1e60514883
remote: -----[ stdin ]-----
remote: {"ref_kind": "branch", "body": "Add b", "author_email": "brobecker@adacore.com", "subject": "Add b", "object_type": "commit", "rev": "4a250d3fd87947c594579e14b5688d1e60514883", "author_name": "Joel Brobecker", "ref_name": "refs/heads/multiple-commits-accept-all-new"}
remote: ---[ end stdin ]---
remote: DEBUG: commit-extra-checker.py refs/heads/multiple-commits-accept-all-new 97ce4ee0f0bbb3a56c5075b9037f4caf1ce5047f
remote: -----[ stdin ]-----
remote: {"ref_kind": "branch", "body": "Add c", "author_email": "brobecker@adacore.com", "subject": "Add c", "object_type": "commit", "rev": "97ce4ee0f0bbb3a56c5075b9037f4caf1ce5047f", "author_name": "Joel Brobecker", "ref_name": "refs/heads/multiple-commits-accept-all-new"}
remote: ---[ end stdin ]---
remote: DEBUG: commit-extra-checker.py refs/heads/multiple-commits-accept-all-new 309196cc8cf49451d8030e4c25013f3791f6a946
remote: -----[ stdin ]-----
remote: {"ref_kind": "branch", "body": "Remove a (not needed anymore)", "author_email": "brobecker@adacore.com", "subject": "Remove a (not needed anymore)", "object_type": "commit", "rev": "309196cc8cf49451d8030e4c25013f3791f6a946", "author_name": "Joel Brobecker", "ref_name": "refs/heads/multiple-commits-accept-all-new"}
remote: ---[ end stdin ]---
remote: DEBUG: Sending email: [repo/multiple-commits-accept-all-new] Add b...
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/multiple-commits-accept-all-new] Add c...
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/multiple-commits-accept-all-new] Remove a (not needed anymore)...
To ../bare/repo.git
   1e1e706..309196c  multiple-commits-accept-all-new -> multiple-commits-accept-all-new
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push a branch which introduces more than one new commit,
        # which we expect the commit-extra-checker to accept.
        #
        # Note that the remote repository was deliberately set up to have
        # a branch named future-multiple-commits-accept-some-preexisting
        # which already includes two of the 3 commits this branch updates.
        # In other words, prior to the push, we have the following layout
        # (left to right is parent to child):
        #
        #     A <-- origin/multiple-commits-accept-some-preexisting
        #       \__ B <-- C <-- origin/future-multiple-commits-accept-some-preexisting
        #                   \__ D <-- multiple-commits-accept-some-preexisting
        #
        # The push will add commits B, C and D to the remote's
        # multiple-commits-accept-some-preexisting branch. The fact the branch
        # future-multiple-commits-accept-some-preexisting already has commits
        # B and C means that those commits shouldn't be checked. This is
        # consistent with the policy that we follow for all the other checks
        # on commits. One extreme example of why this is important is when
        # creating a new branch from an existing one. If the existing branch
        # had a very large number of commits (e.g. the GCC's master branch
        # has ~180,000 commits as of 2020-10-02), it would be as many unwanted
        # calls to the commit checkers!

        p = Run('git push origin multiple-commits-accept-some-preexisting'.split())
        expected_out = """\
remote: DEBUG: commit-extra-checker.py refs/heads/multiple-commits-accept-some-preexisting 25f07c061174291b3126b1df487937ea3408f291
remote: -----[ stdin ]-----
remote: {"ref_kind": "branch", "body": "Really fix `a' this time (I think?!?)", "author_email": "brobecker@adacore.com", "subject": "Really fix `a' this time (I think?!?)", "object_type": "commit", "rev": "25f07c061174291b3126b1df487937ea3408f291", "author_name": "Joel Brobecker", "ref_name": "refs/heads/multiple-commits-accept-some-preexisting"}
remote: ---[ end stdin ]---
remote: DEBUG: Sending email: [repo/multiple-commits-accept-some-preexisting] Modify `a' and add `b'...
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/multiple-commits-accept-some-preexisting] Fix `a' and delete `b' (no longer needed, after all)...
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/multiple-commits-accept-some-preexisting] Really fix `a' this time (I think?!?)...
To ../bare/repo.git
   1e1e706..25f07c0  multiple-commits-accept-some-preexisting -> multiple-commits-accept-some-preexisting
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push a branch which introduces more than one new commit, with
        # the first one expected to be rejected by commit-extra-checker
        # (we should see the checker only be called once).

        p = Run('git push origin multiple-commits-reject-first'.split())
        expected_out = """\
remote: *** The following commit was rejected by your hooks.commit-extra-checker script (status: 1)
remote: *** commit: 8ce0d28d635cd7dd490f6d574baecf079fd363d3
remote: *** DEBUG: commit-extra-checker.py refs/heads/multiple-commits-reject-first 8ce0d28d635cd7dd490f6d574baecf079fd363d3
remote: *** -----[ stdin ]-----
remote: *** {"ref_kind": "branch", "body": "Modify `a' and add `b' (bad-commit)", "author_email": "brobecker@adacore.com", "subject": "Modify `a' and add `b' (bad-commit)", "object_type": "commit", "rev": "8ce0d28d635cd7dd490f6d574baecf079fd363d3", "author_name": "Joel Brobecker", "ref_name": "refs/heads/multiple-commits-reject-first"}
remote: *** ---[ end stdin ]---
remote: *** Error: Invalid bla bla bla. Rejecting Update.
remote: error: hook declined to update refs/heads/multiple-commits-reject-first
To ../bare/repo.git
 ! [remote rejected] multiple-commits-reject-first -> multiple-commits-reject-first (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push a branch which introduces more than one new commit, with
        # the second one (explicitly chosen to not be first nor last)
        # expected to be rejected by commit-extra-checker (we should see
        # the checker  be called exactly twice).
        #
        # Note that the output in which the calls to the checker is
        # printed in the output is out of order. I believe this is Git
        # printing stderr contents ahead of stdout. Accept that
        # pre-existing behavior.

        p = Run('git push origin multiple-commits-reject-middle'.split())
        expected_out = """\
remote: *** The following commit was rejected by your hooks.commit-extra-checker script (status: 1)
remote: *** commit: 6822734adebb636e8d3f9e664215d56f3d319282
remote: *** DEBUG: commit-extra-checker.py refs/heads/multiple-commits-reject-middle 6822734adebb636e8d3f9e664215d56f3d319282
remote: *** -----[ stdin ]-----
remote: *** {"ref_kind": "branch", "body": "Fix `a' and delete `b' (bad-commit)", "author_email": "brobecker@adacore.com", "subject": "Fix `a' and delete `b' (bad-commit)", "object_type": "commit", "rev": "6822734adebb636e8d3f9e664215d56f3d319282", "author_name": "Joel Brobecker", "ref_name": "refs/heads/multiple-commits-reject-middle"}
remote: *** ---[ end stdin ]---
remote: *** Error: Invalid bla bla bla. Rejecting Update.
remote: DEBUG: commit-extra-checker.py refs/heads/multiple-commits-reject-middle 26107593d14c75d8146f24d635a7f3b3a4282e37
remote: -----[ stdin ]-----
remote: {"ref_kind": "branch", "body": "Modify `a' and add `b'", "author_email": "brobecker@adacore.com", "subject": "Modify `a' and add `b'", "object_type": "commit", "rev": "26107593d14c75d8146f24d635a7f3b3a4282e37", "author_name": "Joel Brobecker", "ref_name": "refs/heads/multiple-commits-reject-middle"}
remote: ---[ end stdin ]---
remote: error: hook declined to update refs/heads/multiple-commits-reject-middle
To ../bare/repo.git
 ! [remote rejected] multiple-commits-reject-middle -> multiple-commits-reject-middle (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # multiple-commits-reject-last
        #   + Modify `a' and add `b'
        #   + Fix `a' and delete `b' (no longer needed, after all)
        #   + Really fix `a' this time (bad-commit)

        # Push a branch which introduces more than one new commit, with
        # the second one (explicitly chosen to not be first nor last)
        # expected to be rejected by commit-extra-checker (we should see
        # the checker  be called exactly twice).
        #
        # Note that the output in which the calls to the checker is
        # printed in the output is out of order. I believe this is Git
        # printing stderr contents ahead of stdout. Accept that
        # pre-existing behavior.

        p = Run('git push origin multiple-commits-reject-last'.split())
        expected_out = """\
remote: *** The following commit was rejected by your hooks.commit-extra-checker script (status: 1)
remote: *** commit: d2593aef8aaaef1a6a43336277afe5c02b2fe04e
remote: *** DEBUG: commit-extra-checker.py refs/heads/multiple-commits-reject-last d2593aef8aaaef1a6a43336277afe5c02b2fe04e
remote: *** -----[ stdin ]-----
remote: *** {"ref_kind": "branch", "body": "Really fix `a' this time (bad-commit)", "author_email": "brobecker@adacore.com", "subject": "Really fix `a' this time (bad-commit)", "object_type": "commit", "rev": "d2593aef8aaaef1a6a43336277afe5c02b2fe04e", "author_name": "Joel Brobecker", "ref_name": "refs/heads/multiple-commits-reject-last"}
remote: *** ---[ end stdin ]---
remote: *** Error: Invalid bla bla bla. Rejecting Update.
remote: DEBUG: commit-extra-checker.py refs/heads/multiple-commits-reject-last 37b8b3265f6649a0609d3473f932c55cfbe1b186
remote: -----[ stdin ]-----
remote: {"ref_kind": "branch", "body": "Modify `a' and add `b'", "author_email": "brobecker@adacore.com", "subject": "Modify `a' and add `b'", "object_type": "commit", "rev": "37b8b3265f6649a0609d3473f932c55cfbe1b186", "author_name": "Joel Brobecker", "ref_name": "refs/heads/multiple-commits-reject-last"}
remote: ---[ end stdin ]---
remote: DEBUG: commit-extra-checker.py refs/heads/multiple-commits-reject-last 3df475a99cc07966432aaf471054ead01a7a8cbb
remote: -----[ stdin ]-----
remote: {"ref_kind": "branch", "body": "Fix `a' and delete `b' (no longer needed, after all)", "author_email": "brobecker@adacore.com", "subject": "Fix `a' and delete `b' (no longer needed, after all)", "object_type": "commit", "rev": "3df475a99cc07966432aaf471054ead01a7a8cbb", "author_name": "Joel Brobecker", "ref_name": "refs/heads/multiple-commits-reject-last"}
remote: ---[ end stdin ]---
remote: error: hook declined to update refs/heads/multiple-commits-reject-last
To ../bare/repo.git
 ! [remote rejected] multiple-commits-reject-last -> multiple-commits-reject-last (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push a new branch, and verify that our commit-extra-checker
        # gets called (and rejects the push because of a bad commit).

        p = Run('git push origin new-branch-multiple-commits-reject-first'
                .split())
        expected_out = """\
remote: *** The following commit was rejected by your hooks.commit-extra-checker script (status: 1)
remote: *** commit: 8ce0d28d635cd7dd490f6d574baecf079fd363d3
remote: *** DEBUG: commit-extra-checker.py refs/heads/new-branch-multiple-commits-reject-first 8ce0d28d635cd7dd490f6d574baecf079fd363d3
remote: *** -----[ stdin ]-----
remote: *** {"ref_kind": "branch", "body": "Modify `a' and add `b' (bad-commit)", "author_email": "brobecker@adacore.com", "subject": "Modify `a' and add `b' (bad-commit)", "object_type": "commit", "rev": "8ce0d28d635cd7dd490f6d574baecf079fd363d3", "author_name": "Joel Brobecker", "ref_name": "refs/heads/new-branch-multiple-commits-reject-first"}
remote: *** ---[ end stdin ]---
remote: *** Error: Invalid bla bla bla. Rejecting Update.
remote: error: hook declined to update refs/heads/new-branch-multiple-commits-reject-first
To ../bare/repo.git
 ! [remote rejected] new-branch-multiple-commits-reject-first -> new-branch-multiple-commits-reject-first (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        self.assertNotEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)

        # Push a branch deletion. Our commit-extra-checker shouldn't
        # get called, since there are no new commits.

        p = Run('git push origin :delete-me'.split())
        expected_out = """\
remote: DEBUG: Sending email: [repo] Deleted branch 'delete-me'...
To ../bare/repo.git
 - [deleted]         delete-me
"""

        self.assertEqual(p.status, 0, p.image)
        self.assertRunOutputEqual(p, expected_out)


if __name__ == '__main__':
    runtests()
