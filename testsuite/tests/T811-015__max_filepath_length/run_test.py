from support import *


class TestRun(TestCase):
    def test_push_commits(testcase):
        cd("%s/repo" % TEST_DIR)

        # For this testcase, the contents of the emails being sent
        # is not important, so reduce their verbosity.
        testcase.change_email_sending_verbosity(full_verbosity=False)

        #################################################################
        # Push a commit which does the following:
        #  - Introduces new files, with their path length being within
        #    this repository's limit;
        #  - Modifies some existing files, whose path length exceed
        #    this repository's limits. Because those files existed
        #    already prior to this commit, the git-hooks should still
        #    accept this change.
        #  - As the name of the branch indicates, the branch already
        #    exists in the remote (so, this is a branch update, not
        #    a branch creation).
        #################################################################

        p = testcase.run("git push origin existing-branch-ok".split())
        expected_out = """\
remote: *** cvs_check: `file_67' (7 chars)
remote: *** cvs_check: `file_with_name_too_long' (23 chars)
remote: DEBUG: Sending email: [repo/existing-branch-ok] Add file_67 and edit (existing) file_with_name_too_long...
To ../bare/repo.git
   40f4f7d..3b98690  existing-branch-ok -> existing-branch-ok
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        #################################################################
        # Push a commit which does the following:
        #  - Modifies an existing file with their path name within
        #    acceptable limits
        #  - Create a new file whose path name is exactly at the maximum
        #    acceptable limit;
        #  - Create one new file whose path name is one character longer
        #    that the previous file, and therefore should be rejected
        #    by the hooks.
        #  - As the name of the branch indicates, the branch already
        #    exists in the remote (so, this is a branch update, not
        #    a branch creation).
        #################################################################

        p = testcase.run("git push origin existing-branch-one-bad".split())
        expected_out = """\
remote: *** The following commit introduces some new files whose total
remote: *** path length exceeds the maximum allowed for this repository.
remote: *** Please re-do your commit choosing shorter paths for those new
remote: *** files, or contact your repository administrator if you believe
remote: *** the limit should be raised.
remote: ***
remote: ***     Commit: c6c5db8bad4c0ab41e0ad9c19cf667d2994f5047
remote: ***     Subject: Add/Modify two OK files, and add one file with name too long
remote: ***
remote: *** The problematic files are (12 characters max):
remote: ***
remote: ***     bad_56789_123 (13 characters)
remote: ***
remote: error: hook declined to update refs/heads/existing-branch-one-bad
To ../bare/repo.git
 ! [remote rejected] existing-branch-one-bad -> existing-branch-one-bad (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        #################################################################
        # Push a commit which is very similar to the commit above
        # on branch existing-branch-one-bad, with the difference being:
        #  - Instead of creating one file whose path length exceeds
        #    the maximum, the commit introduces multiple such files.
        #    The purpose of this test is to verify that all such files
        #    are flagged and that the complete list is shown to the user.
        #    Note that one of such files is inside a directory, and while
        #    the length of its basename is within limits, the total path
        #    itself is just one character over.
        #  - As the name of the branch indicates, the branch already
        #    exists in the remote (so, this is a branch update, not
        #    a branch creation).
        #################################################################

        p = testcase.run("git push origin existing-branch-multi-bad".split())
        expected_out = """\
remote: *** The following commit introduces some new files whose total
remote: *** path length exceeds the maximum allowed for this repository.
remote: *** Please re-do your commit choosing shorter paths for those new
remote: *** files, or contact your repository administrator if you believe
remote: *** the limit should be raised.
remote: ***
remote: ***     Commit: 89ef692bfa197c2aaf9e57a06f273740e65f9ea3
remote: ***     Subject: Some OK, and a couple too long.
remote: ***
remote: *** The problematic files are (12 characters max):
remote: ***
remote: ***     bad_56789_123 (13 characters)
remote: ***     dir/bad_9_123 (13 characters)
remote: ***
remote: error: hook declined to update refs/heads/existing-branch-multi-bad
To ../bare/repo.git
 ! [remote rejected] existing-branch-multi-bad -> existing-branch-multi-bad (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        #################################################################
        # Push a commit which does the following:
        #  - Introduces new files, with their path length being within
        #    this repository's limit; One of those files is precisely
        #    at the limit, which allows us to verify that we're not
        #    being stricter than required.
        #  - As the name of the branch indicates, the branch does not
        #    exist in the remote yet (this is a "first commit" for
        #    a new branch).
        #################################################################

        p = testcase.run("git push origin new-branch-ok".split())
        expected_out = """\
remote: *** cvs_check: `file_6' (6 chars)
remote: *** cvs_check: `file_67' (7 chars)
remote: *** cvs_check: `ok_456789_12' (12 chars)
remote: DEBUG: Sending email: [repo] Created branch 'new-branch-ok'...
remote: DEBUG: inter-email delay...
remote: DEBUG: Sending email: [repo/new-branch-ok] Initial commit....
To ../bare/repo.git
 * [new branch]      new-branch-ok -> new-branch-ok
"""

        testcase.assertEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        #################################################################
        # Push a commit which does the following:
        #  - Create a new file whose path name is exactly at the maximum
        #    acceptable limit;
        #  - Create one new file whose path name is one character longer
        #    that the previous file, and therefore should be rejected
        #    by the hooks.
        #  - As the name of the branch indicates, the branch does not
        #    exist in the remote yet (this is a "first commit" for
        #    a new branch).
        #################################################################

        p = testcase.run("git push origin new-branch-one-bad".split())
        expected_out = """\
remote: *** The following commit introduces some new files whose total
remote: *** path length exceeds the maximum allowed for this repository.
remote: *** Please re-do your commit choosing shorter paths for those new
remote: *** files, or contact your repository administrator if you believe
remote: *** the limit should be raised.
remote: ***
remote: ***     Commit: a283bacdcc73e9066a542c1aedaeb7442f087bfb
remote: ***     Subject: Initial commit (with one file too long)
remote: ***
remote: *** The problematic files are (12 characters max):
remote: ***
remote: ***     bad_56789_123 (13 characters)
remote: ***
remote: error: hook declined to update refs/heads/new-branch-one-bad
To ../bare/repo.git
 ! [remote rejected] new-branch-one-bad -> new-branch-one-bad (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)

        #################################################################
        # Push a commit which is very similar to the commit above
        # on branch new-branch-one-bad, with the difference being:
        #  - Instead of creating one file whose path length exceeds
        #    the maximum, the commit introduces multiple such files.
        #    The purpose of this test is to verify that all such files
        #    are flagged and that the complete list is shown to the user.
        #    Note that one of such files is inside a directory, and while
        #    the length of its basename is within limits, the total path
        #    itself is just one character over.
        #  - As the name of the branch indicates, the branch does not
        #    exist in the remote yet (this is a "first commit" for
        #    a new branch).
        #################################################################

        p = testcase.run("git push origin new-branch-multi-bad".split())
        expected_out = """\
remote: *** The following commit introduces some new files whose total
remote: *** path length exceeds the maximum allowed for this repository.
remote: *** Please re-do your commit choosing shorter paths for those new
remote: *** files, or contact your repository administrator if you believe
remote: *** the limit should be raised.
remote: ***
remote: ***     Commit: e00b7acd65d20eb0914d70cbb29b7d0808b36fb4
remote: ***     Subject: Initial commit.
remote: ***
remote: *** The problematic files are (12 characters max):
remote: ***
remote: ***     bad_56789_123 (13 characters)
remote: ***     dir/bad_9_123 (13 characters)
remote: ***     file_with_name_too_long (23 characters)
remote: ***
remote: error: hook declined to update refs/heads/new-branch-multi-bad
To ../bare/repo.git
 ! [remote rejected] new-branch-multi-bad -> new-branch-multi-bad (hook declined)
error: failed to push some refs to '../bare/repo.git'
"""

        testcase.assertNotEqual(p.status, 0, p.image)
        testcase.assertRunOutputEqual(p, expected_out)


if __name__ == "__main__":
    runtests()
